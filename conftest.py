import pytest
import time
import random
from playwright.sync_api import Page, BrowserContext

# Тестовые данные
TEST_USER = {
    "email": "afpcp75@gmail.com",
    "password": "21052006Zandem?",
    "full_name": "ЗА Землянкин Андрей"  
}

TEST_USER_2 = {
    "email": "zandemandrej@gmail.com",
    "password": "21052006Zandem?",
    "full_name": "А2 Андрей 2"
}


@pytest.fixture
def test_user():
    """Возвращает тестовые данные пользователя"""
    return TEST_USER

@pytest.fixture
def disposable_user():
    return TEST_USER_2


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """Создаёт новую страницу для каждого теста"""
    page = context.new_page()
    yield page
    page.close()


def unique_name(base="Проект"):
    """Генерирует уникальное имя проекта"""
    return f"{base} {int(time.time())}{random.randint(10, 99)}"


def unique_code(prefix="AT"):
    """Генерирует уникальный код проекта (4 цифры)"""
    return f"{prefix}{int(time.time()) % 10000:04d}"
