import pytest
from playwright.sync_api import Page, BrowserContext

# Тестовые данные (можно вынести в отдельный файл или переменные окружения)
TEST_USER = {
    "email": "afpcp75@gmail.com",
    "password": "21052006Zandem?",
    "full_name": "ЗА Землянкин Андрей"  # имя, которое отображается в меню
}


@pytest.fixture
def test_user():
    """Возвращает тестовые данные пользователя"""
    return TEST_USER

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """Создаёт новую страницу для каждого теста"""
    page = context.new_page()
    yield page
    page.close()
