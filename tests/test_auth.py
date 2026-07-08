import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage

# Позитивные тесты

def test_tc_1_1_successful_login(page, test_user):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user["email"], test_user["password"])
    login_page.check_successful_login(test_user["full_name"])


def test_tc_1_3_logout(page, test_user):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user["email"], test_user["password"])
    login_page.check_successful_login(test_user["full_name"])

    # Выход
    page.get_by_role("link", name=test_user["full_name"]).click()
    page.get_by_text("Выход").click()

    # Проверяем, что перенаправило на страницу входа
    expect(page.get_by_role("textbox", name="Электронная почта")).to_be_visible()


# Негативные тесты

def test_tc_1_4_invalid_email(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("nonexistent@gmail.com", "21052006Zandem?")
    login_page.check_error_message("Логин или пароль указаны неверно")


def test_tc_1_5_invalid_password(page, test_user):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user["email"], "wrongpassword")
    login_page.check_error_message("Пароль не подходит")


def test_tc_1_6_empty_fields(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login_button.click()
    # Проверяем, что появилось сообщение об ошибке
    error_text = page.get_by_text("Введи логин в формате электронной почты")
    expect(error_text).to_be_visible()
    # можно также проверить, что кнопка Войти осталась активной или неактивной, но это опционально