import re
import pytest
import os
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from playwright.sync_api import expect


@pytest.fixture
def login_and_open_profile(page, test_user):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user["email"], test_user["password"])
    # Ожидаем ссылку на пользователя по частичному совпадению (без инициалов)
    parts = test_user["full_name"].split()
    if len(parts) >= 2:
        search_text = " ".join(parts[1:])
    else:
        search_text = test_user["full_name"]
    page.get_by_role("link").filter(has_text=search_text).wait_for(state="visible", timeout=30000)
    profile_page = ProfilePage(page)
    profile_page.open_profile(test_user["full_name"])
    return profile_page

@pytest.fixture
def disposable_login_and_open_profile(page, disposable_user):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(disposable_user["email"], disposable_user["password"])
    
    # Ждём успешного входа (появление ссылки с именем пользователя)
    parts = disposable_user["full_name"].split()
    if len(parts) >= 2:
        search_text = " ".join(parts[1:])
    else:
        search_text = disposable_user["full_name"]
    page.get_by_role("link").filter(has_text=search_text).wait_for(state="visible", timeout=30000)
    
    profile_page = ProfilePage(page)
    profile_page.open_profile(disposable_user["full_name"])
    return profile_page


# Положительные ТК


def test_tc_4_1_view_own_profile(page, login_and_open_profile):
    """ТК-4.1 Просмотр собственного профиля."""
    field_labels = [
        "ФИО", "Должность", "Город", "Дата рождения", "Номер телефона",
        "Электронная почта", "Компания", "Руководитель", "Адрес офиса", "Подразделение",
    ]
    for label in field_labels:
        expect(page.get_by_text(label, exact=False).first).to_be_visible()


def test_tc_4_2_edit_full_name(page, login_and_open_profile, test_user):
    """
    ТК-4.2 Редактирование ФИО (обязательное поле).
    Тест реально меняет ФИО, затем возвращает обратно, чтобы не ломать фикстуру.
    """
    profile_page = login_and_open_profile
    original_full_name = test_user["full_name"].split(" ", 1)[-1]

    profile_page.edit_field(0, "Иванов Иван Иванович")
    page.reload()
    expect(page.get_by_text("Иванов Иван Иванович", exact=False)).to_be_visible(timeout=10000)

    # откатываем
    profile_page.edit_field(0, original_full_name)
    page.reload()
    expect(page.get_by_role("link", name=original_full_name)).to_be_visible(timeout=10000)


def test_tc_4_3_edit_position(page, login_and_open_profile):
    """ТК-4.3 Редактирование должности."""
    profile_page = login_and_open_profile
    profile_page.edit_field(1, "Тестировщик")
    expect(page.get_by_text("Тестировщик", exact=False)).to_be_visible(timeout=10000)


def test_tc_4_4_edit_city(page, login_and_open_profile):
    """ТК-4.4 Редактирование города."""
    profile_page = login_and_open_profile
    profile_page.edit_field(2, "Москва")
    expect(page.get_by_text("Москва", exact=False)).to_be_visible(timeout=10000)


def test_tc_4_5_change_avatar(page, login_and_open_profile):
    profile_page = login_and_open_profile
    avatar_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "avatar.png")
    assert os.path.exists(avatar_path), f"Файл {avatar_path} не найден"
    profile_page.change_avatar(avatar_path)
    expect(profile_page.avatar_large).to_be_visible(timeout=10000)


def test_tc_4_6_change_password_success(page, login_and_open_profile, test_user):
    profile_page = login_and_open_profile
    old_password = test_user["password"]
    # Пароль, который точно соответствует требованиям (добавляем 1 в конец)
    new_password = old_password + "1"
    try:
        profile_page.change_password(old_password, new_password)
        expect(page.get_by_text("Пароль успешно изменён.", exact=False)).to_be_visible(timeout=10000)
        page.reload()
        # Возвращаем старый пароль
        profile_page.change_password(new_password, old_password)
        expect(page.get_by_text("Пароль успешно изменён.", exact=False)).to_be_visible(timeout=10000)
        page.reload()
    except Exception:
        # Если тест упал, пытаемся вернуть пароль, чтобы не ломать другие тесты
        try:
            profile_page.change_password(new_password, old_password)
        except:
            pass
        raise


def test_tc_4_7_set_absence_period(page, login_and_open_profile):
    """ТК-4.7 Установка периода отсутствия."""
    profile_page = login_and_open_profile
    profile_page.set_absence("1", "16")
    expect(page.get_by_text("Недоступен", exact=False)).to_be_visible(timeout=10000)


def test_tc_4_8_remove_absence_period(page, login_and_open_profile):
    """ТК-4.8 Удаление периода отсутствия."""
    profile_page = login_and_open_profile
    profile_page.set_absence("1", "16")
    profile_page.remove_absence()
    expect(page.get_by_text("Доступен", exact=False)).to_be_visible(timeout=10000)


@pytest.mark.skip(
    reason="Тест НЕОБРАТИМО удаляет учётную запись. Запускать только на отдельном одноразовом аккаунте."
)
def test_tc_4_9_delete_account_no_owned_spaces(page, disposable_login_and_open_profile, disposable_user):
    """
    ТК-4.9 Удаление учётной записи (при отсутствии пространств во владении).
    Внимание: тест НЕОБРАТИМО удаляет аккаунт disposable_user.
    Убедитесь, что у этого аккаунта нет пространств, иначе удаление не пройдёт.
    """
    profile_page = disposable_login_and_open_profile
    profile_page.open_delete_account_dialog()
    profile_page.delete_account(disposable_user["email"], reason="Тестовое удаление")
    expect(page).to_have_url(re.compile(r".*/(sign-?in|login)"), timeout=10000)

# Отрицательные ТК


def test_tc_4_10_empty_full_name(page, login_and_open_profile):
    """ТК-4.10 Попытка сохранить пустое ФИО (обязательное поле)."""
    profile_page = login_and_open_profile
    field = profile_page.editable_fields.first
    field.click()
    textbox = page.get_by_role("textbox", name="Заполнить")
    textbox.fill("")
    textbox.press("Enter")
    expect(page.get_by_text("Не удалось обновить данные пользователя", exact=False)).to_be_visible(timeout=10000)


def test_tc_4_11_change_password_wrong_old(page, login_and_open_profile, test_user):
    profile_page = login_and_open_profile
    # Вводим неверный старый пароль
    profile_page.change_password("wrong_old_password_123", "NewPassword123!")
    # Проверяем появление сообщения об ошибке
    expect(page.get_by_text("Не удалось изменить пароль. Возможно указан неверный старый пароль.", exact=False)).to_be_visible(timeout=10000)


def test_tc_4_12_change_password_weak(page, login_and_open_profile, test_user):
    """ТК-4.12 Изменение пароля с нарушением требований."""
    profile_page = login_and_open_profile
    profile_page.open_change_password_dialog()
    profile_page.old_password_input.fill(test_user["password"])
    profile_page.new_password_input.fill("123")
    profile_page.confirm_password_input.fill("123")
    expect(profile_page.change_password_button).to_be_disabled(timeout=10000)


def test_tc_4_13_delete_account_as_owner(page, login_and_open_profile):
    """ТК-4.13 Попытка удалить аккаунт, будучи владельцем пространства, без передачи прав."""
    profile_page = login_and_open_profile
    profile_page.open_delete_account_dialog()
    # Ожидаем сообщение о необходимости назначить другого владельца
    expect(page.get_by_text("назначь другого владельца", exact=False)).to_be_visible(timeout=10000)


def test_tc_4_14_delete_account_wrong_email(page, disposable_login_and_open_profile):
    """
    ТК-4.14 Подтверждение удаления профиля с неверным email.
    Ожидаемый результат: кнопка "Удалить" неактивна.
    """
    profile_page = disposable_login_and_open_profile
    profile_page.open_delete_account_dialog()
    profile_page.final_delete_button.click()
    profile_page.delete_confirm_input.fill("wrong@mail.com")
    expect(profile_page.final_delete_button).to_be_disabled(timeout=5000)