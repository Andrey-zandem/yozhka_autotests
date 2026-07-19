import pytest
import os
from pages.login_page import LoginPage
from pages.project_page import ProjectPage
from playwright.sync_api import expect
from conftest import unique_name, unique_code


@pytest.fixture
def login_and_navigate(page, test_user):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user["email"], test_user["password"])
    page.get_by_role("link", name=test_user["full_name"]).wait_for(state="visible", timeout=30000)
    project_page = ProjectPage(page)
    project_page.navigate_to_projects_tab()
    return project_page

# Положительные ТК

def test_tc_3_1_create_project_success(page, login_and_navigate):
    """ТК-3.1 Создание проекта с корректными данными."""
    project_page = login_and_navigate
    name = unique_name()
    project_page.create_project(name)
    expect(project_page.get_project_link(name)).to_be_visible()
    project_page.delete_project(name)


def test_tc_3_2_rename_project(page, login_and_navigate):
    """ТК-3.2 Изменение названия проекта."""
    project_page = login_and_navigate
    name = unique_name()
    new_name = unique_name()
    project_page.create_project(name)
    project_page.rename_project(new_name)
    # название должно обновиться и в меню навигации, и на доске
    expect(project_page.get_project_link(new_name)).to_be_visible(timeout=10000)
    expect(project_page.get_project_link(name)).not_to_be_visible()
    project_page.delete_project(new_name)

def test_tc_3_3_change_icon(page, login_and_navigate):
    """ТК-3.3 Изменение иконки проекта."""
    project_page = login_and_navigate
    name = unique_name()
    project_page.create_project(name)
    project_page.change_icon(name)
    # Проверяем появление сообщения об успехе
    success_message = page.get_by_text("Иконка проекта изменена успешно", exact=False)
    expect(success_message).to_be_visible(timeout=10000)
    project_page.delete_project(name)


def test_tc_3_4_archive_project(page, login_and_navigate):
    """ТК-3.4 Архивирование проекта."""
    project_page = login_and_navigate
    name = unique_name()
    project_page.create_project(name)
    project_page.archive_project(name)
    project_page.restore_project(name)
    project_page.delete_project(name)


def test_tc_3_5_restore_project(page, login_and_navigate):
    """ТК-3.5 Восстановление проекта из архива."""
    project_page = login_and_navigate
    name = unique_name()
    project_page.create_project(name)
    project_page.archive_project(name)
    project_page.restore_project(name)
    project_page.delete_project(name)


def test_tc_3_6_delete_project(page, login_and_navigate):
    """ТК-3.6 Удаление проекта."""
    project_page = login_and_navigate
    name = unique_name()
    project_page.create_project(name)
    project_page.delete_project(name)


def test_tc_3_7_add_to_favorites(page, login_and_navigate):
    """ТК-3.7 Добавление проекта в избранное."""
    project_page = login_and_navigate
    name = unique_name()
    project_page.create_project(name)
    project_page.add_to_favorites(name)
    project_page.delete_project(name)


def test_tc_3_8_remove_from_favorites(page, login_and_navigate):
    """ТК-3.8 Удаление проекта из избранного."""
    project_page = login_and_navigate
    name = unique_name()
    project_page.create_project(name)
    project_page.add_to_favorites(name)
    project_page.remove_from_favorites(name)
    project_page.delete_project(name)


# Отрицательные ТК

def test_tc_3_9_create_project_empty_name(page, login_and_navigate):
    """ТК-3.9 Создание проекта с пустым названием."""
    project_page = login_and_navigate
    project_page.open_create_project_modal()
    project_page.project_name_input.fill("")
    expect(project_page.create_button).to_be_disabled()


def test_tc_3_10_create_project_invalid_code(page, login_and_navigate):
    """ТК-3.10 Создание проекта с невалидным кодом (с пробелами)."""
    project_page = login_and_navigate
    project_page.open_create_project_modal()
    project_page.project_name_input.fill("Тест")
    project_page.page.click("body")
    project_page.open_code_field_button.click()
    project_page.project_code_input.wait_for(state="visible", timeout=30000)
    project_page.project_code_input.fill("T P")
    expect(project_page.create_button).to_be_disabled()


def test_tc_3_11_create_project_as_member(page, disposable_user):
    """ТК-3.11 Попытка создания проекта участником (без прав)."""
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(disposable_user["email"], disposable_user["password"])
    project_page = ProjectPage(page)
    project_page.navigate_to_projects_tab()
    expect(project_page.create_project_button).not_to_be_visible()


# для этого теста нужен заранее созданный проект с именем Тест
def test_tc_3_12_delete_project_as_member(page, disposable_user, test_user):
    """ТК-3.12 Попытка удалить проект участником."""
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(disposable_user["email"], disposable_user["password"])
    project_page = ProjectPage(page)
    project_page.navigate_to_projects_tab()
    name = "Тест"
    project_page.get_project_link(name).hover()
    more_button = project_page.get_project_link(name).get_by_test_id("iconButton")
    more_button.click()
    expect(page.get_by_text("Удалить", exact=True)).not_to_be_visible()


def test_tc_3_13_archive_with_wrong_code(page, login_and_navigate):
    """ТК-3.13 Архивирование проекта с неверным кодом (подтверждение)."""
    project_page = login_and_navigate
    name = unique_name()
    project_page.create_project(name)
    project_page.open_project(name)
    project_page.open_board_menu(name)
    project_page.page.get_by_text("Архивировать").click()
    confirm_input = project_page.page.get_by_role("textbox")
    confirm_input.fill("WRONG")
    expect(project_page.page.get_by_role("button", name="Архивировать")).to_be_disabled()