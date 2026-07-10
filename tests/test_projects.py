import pytest
from pages.login_page import LoginPage
from pages.project_page import ProjectPage
from playwright.sync_api import expect

# Фикстура test_user определена в conftest.py


@pytest.fixture(autouse=True)
def login_and_navigate(page, test_user):
    """Авторизация и переход к проектам перед каждым тестом"""
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user["email"], test_user["password"])
    login_page.check_successful_login(test_user["full_name"])
    # Переходим на вкладку "Проекты"
    project_page = ProjectPage(page)
    project_page.navigate_to_projects_tab()
    # Возвращаем project_page для использования в тестах
    return project_page


# ----------------------------------------------------------------------
# Позитивные тесты
# ----------------------------------------------------------------------

def test_tc_3_1_create_project_success(page, login_and_navigate):
    """
    ТК-3.1: Создание проекта с корректными данными
    Ожидаемый результат: проект создан, отображается в списке.
    """
    project_page = login_and_navigate
    project_name = "Автотест Проект"
    project_code = "ATP"
    project_page.create_project(project_name, project_code)
    project_page.check_success_message("Проект успешно создан")
    # Проверяем, что проект появился в списке
    expect(project_page.get_project_item(project_name)).to_be_visible()


def test_tc_3_2_rename_project(page, login_and_navigate):
    """
    ТК-3.2: Изменение названия проекта
    Ожидаемый результат: название обновлено.
    """
    project_page = login_and_navigate
    old_name = "Автотест Проект"
    new_name = "Автотест Проект (переименован)"
    # Сначала создадим проект
    project_page.create_project(old_name, "ATP")
    # Переименовываем
    project_page.rename_project(old_name, new_name)
    project_page.check_success_message("Название проекта изменено")
    # Проверяем, что старое имя исчезло, новое появилось
    expect(project_page.get_project_item(old_name)).not_to_be_visible()
    expect(project_page.get_project_item(new_name)).to_be_visible()


def test_tc_3_4_archive_project(page, login_and_navigate):
    """
    ТК-3.4: Архивирование проекта
    Ожидаемый результат: проект перемещён в архив.
    """
    project_page = login_and_navigate
    project_name = "Автотест Проект Архив"
    project_code = "ATPA"
    project_page.create_project(project_name, project_code)
    # Архивируем
    project_page.archive_project(project_name, project_code)
    project_page.check_success_message("Проект перемещён в архив")
    # Проверяем, что проект исчез из активных и появился в архиве
    expect(project_page.get_project_item(project_name)).not_to_be_visible()
    # Переходим на вкладку проектов для просмотра архива
    project_page.navigate_to_projects_tab()
    expect(project_page.archive_block.locator(f".project-card:has-text('{project_name}')")).to_be_visible()


def test_tc_3_5_restore_project(page, login_and_navigate):
    """
    ТК-3.5: Восстановление проекта из архива
    Ожидаемый результат: проект возвращён в активные.
    """
    project_page = login_and_navigate
    project_name = "Автотест Проект Восстановление"
    project_code = "ATPV"
    project_page.create_project(project_name, project_code)
    project_page.archive_project(project_name, project_code)
    # Восстанавливаем
    project_page.restore_project(project_name)
    project_page.check_success_message("Проект восстановлен")
    # Проверяем, что проект появился в активных
    expect(project_page.get_project_item(project_name)).to_be_visible()


def test_tc_3_6_delete_project(page, login_and_navigate):
    """
    ТК-3.6: Удаление проекта
    Ожидаемый результат: проект удалён безвозвратно.
    """
    project_page = login_and_navigate
    project_name = "Автотест Проект Удаление"
    project_code = "ATPD"
    project_page.create_project(project_name, project_code)
    project_page.delete_project(project_name, project_code)
    project_page.check_success_message("Проект удалён")
    expect(project_page.get_project_item(project_name)).not_to_be_visible()


def test_tc_3_7_add_to_favorites(page, login_and_navigate):
    """
    ТК-3.7: Добавление проекта в избранное
    Ожидаемый результат: проект отмечен звездой.
    """
    project_page = login_and_navigate
    project_name = "Автотест Проект Избранное"
    project_code = "ATPF"
    project_page.create_project(project_name, project_code)
    project_page.add_to_favorites(project_name)
    project_page.check_success_message("Проект добавлен в избранное")
    # Проверяем, что у проекта появилась звезда (ищем класс или атрибут)
    starred_project = project_page.get_project_item(project_name).locator(".star-icon")
    expect(starred_project).to_be_visible()


def test_tc_3_8_remove_from_favorites(page, login_and_navigate):
    """
    ТК-3.8: Удаление проекта из избранного
    Ожидаемый результат: звезда исчезает.
    """
    project_page = login_and_navigate
    project_name = "Автотест Проект Избранное"
    project_code = "ATPF"
    project_page.create_project(project_name, project_code)
    project_page.add_to_favorites(project_name)
    project_page.remove_from_favorites(project_name)
    project_page.check_success_message("Проект убран из избранного")
    starred_project = project_page.get_project_item(project_name).locator(".star-icon")
    expect(starred_project).not_to_be_visible()


# ----------------------------------------------------------------------
# Негативные тесты
# ----------------------------------------------------------------------

def test_tc_3_9_create_project_empty_name(page, login_and_navigate):
    """
    ТК-3.9: Создание проекта с пустым названием
    Ожидаемый результат: кнопка неактивна, поле подсвечено.
    """
    project_page = login_and_navigate
    project_page.open_create_project_modal()
    # Оставляем название пустым
    project_page.project_name_input.fill("")
    # Кнопка должна быть неактивна (атрибут disabled или класс)
    expect(project_page.create_button).to_be_disabled()


def test_tc_3_10_create_project_invalid_code(page, login_and_navigate):
    """
    ТК-3.10: Создание проекта с невалидным кодом (с пробелами)
    Ожидаемый результат: ошибка, проект не создан.
    """
    project_page = login_and_navigate
    project_page.open_create_project_modal()
    project_page.project_name_input.fill("Тест")
    project_page.project_code_input.fill("T P")  # содержит пробел
    project_page.create_button.click()
    project_page.check_error_message("Код должен содержать только латинские буквы и цифры без пробелов")
    # Проверяем, что проект не создался (модалка не закрылась)
    expect(project_page.project_name_input).to_be_visible()


def test_tc_3_11_create_project_as_member(page, test_user):
    """
    ТК-3.11: Попытка создания проекта участником (без прав)
    Ожидаемый результат: кнопка отсутствует.
    """
    # Здесь нужно переключиться на аккаунт с ролью "Участник"
    # Так как у нас один пользователь, этот тест можно пропустить или использовать другого пользователя.
    pytest.skip("Требуется аккаунт с ролью 'Участник' для выполнения теста.")


def test_tc_3_12_delete_project_as_member(page, test_user):
    """
    ТК-3.12: Попытка удалить проект участником
    Ожидаемый результат: пункт удаления отсутствует.
    """
    pytest.skip("Требуется аккаунт с ролью 'Участник' для выполнения теста.")


def test_tc_3_13_archive_with_wrong_code(page, login_and_navigate):
    """
    ТК-3.13: Архивирование проекта с неверным кодом подтверждения
    Ожидаемый результат: кнопка неактивна, архивация не выполняется.
    """
    project_page = login_and_navigate
    project_name = "Автотест Архив Ошибка"
    project_code = "ATAO"
    project_page.create_project(project_name, project_code)
    # Пытаемся заархивировать с неверным кодом
    project_page.open_project_menu(project_name)
    project_page.archive_option.click()
    confirm_input = project_page.page.get_by_role("textbox")
    confirm_input.fill("WRONG")
    # Кнопка должна быть неактивна
    expect(project_page.page.get_by_role("button", name="Архивировать")).to_be_disabled()