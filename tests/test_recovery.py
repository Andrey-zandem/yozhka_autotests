import pytest
from pages.recovery_page import RecoveryPage
from pages.login_page import LoginPage
from playwright.sync_api import expect

# ----------------------------------------------------------------------
# Позитивные тесты
# ----------------------------------------------------------------------

def test_tc_2_1_request_reset_valid_email(page, test_user):
    """
    ТК-2.1: Запрос на восстановление доступа с корректной почтой
    Ожидаемый результат: отображается сообщение 'перейди по ссылке в письме'.
    """
    recovery_page = RecoveryPage(page)
    login_page = LoginPage(page)
    login_page.navigate()
    recovery_page.navigate_to_recovery()
    recovery_page.request_password_reset(test_user["email"])
    recovery_page.check_success_message()


def test_tc_2_4_return_to_login(page):
    """
    ТК-2.4: Возвращение на страницу авторизации
    Ожидаемый результат: перенаправление обратно на страницу входа.
    """
    recovery_page = RecoveryPage(page)
    login_page = LoginPage(page)
    login_page.navigate()
    recovery_page.navigate_to_recovery()
    recovery_page.go_back_to_login()
    # Проверяем, что снова видно поле ввода логина
    expect(page.get_by_role("textbox", name="Электронная почта")).to_be_visible()


# ----------------------------------------------------------------------
# Негативные тесты
# ----------------------------------------------------------------------

def test_tc_2_6_request_reset_empty_email(page):
    """
    ТК-2.6: Запрос на восстановление доступа с пустой почтой
    Ожидаемый результат: поле подсвечено, сообщение об ошибке.
    """
    recovery_page = RecoveryPage(page)
    login_page = LoginPage(page)
    login_page.navigate()
    recovery_page.navigate_to_recovery()
    recovery_page.request_password_reset("")
    recovery_page.check_empty_field_error()


# ----------------------------------------------------------------------
# Пропущенные тесты (требуют перехода по ссылке из письма)
# ----------------------------------------------------------------------

@pytest.mark.skip(reason="Для выполнения требуется перейти по ссылке из письма (недоступно в автотестах)")
def test_tc_2_2_reset_with_valid_password(page):
    pass

@pytest.mark.skip(reason="Для выполнения требуется перейти по ссылке из письма (недоступно в автотестах)")
def test_tc_2_3_display_password_requirements(page):
    pass

@pytest.mark.skip(reason="Для выполнения требуется перейти по ссылке из письма (недоступно в автотестах)")
def test_tc_2_5_reset_with_invalid_password(page):
    pass