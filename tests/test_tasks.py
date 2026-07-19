import pytest
import re
from pages.login_page import LoginPage
from pages.project_page import ProjectPage
from pages.task_page import TaskPage
from playwright.sync_api import expect
from conftest import unique_name


@pytest.fixture
def login_and_create_project(page, test_user):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user["email"], test_user["password"])
    page.get_by_role("link", name=test_user["full_name"]).wait_for(state="visible", timeout=30000)
    project_page = ProjectPage(page)
    project_page.navigate_to_projects_tab()
    project_name = unique_name()
    project_page.create_project(project_name)
    project_page.navigate_to_projects_tab()
    task_page = TaskPage(page)
    return project_page, task_page, project_name


def test_tc_5_1_create_task_global(page, login_and_create_project):
    project_page, task_page, project_name = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name, description="Тестовое описание")
    project_page.open_project(project_name)
    expect(task_page.task_card(task_name)).to_be_visible(timeout=15000)
    project_page.delete_project(project_name)


def test_tc_5_2_create_task_in_column(page, login_and_create_project):
    project_page, task_page, project_name = login_and_create_project
    task_name = unique_name("Задача")
    project_page.open_project(project_name)
    task_page.create_task_in_column(task_name)
    expect(task_page.task_card(task_name)).to_be_visible()
    project_page.delete_project(project_name)


def test_tc_5_3_create_task_in_all_tasks(page, login_and_create_project):
    project_page, task_page, project_name = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task_in_all_tasks(task_name, project_name)
    project_page.open_project(project_name)
    expect(task_page.task_card(task_name)).to_be_visible()
    project_page.delete_project(project_name)


def test_tc_5_4_edit_task_name(page, login_and_create_project):
    project_page, task_page, project_name = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    new_name = "Переименовано " + task_name
    project_page.open_project(project_name)
    task_page.edit_task_name(task_name, new_name)
    expect(task_page.task_card(new_name)).to_be_visible()
    project_page.delete_project(project_name)


def test_tc_5_5_change_status_in_card(page, login_and_create_project):
    project_page, task_page, project_name = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    project_page.open_project(project_name)
    task_page.change_status(task_name, "В работе")
    column = task_page.get_column_by_status("В работе")
    expect(column.locator(task_page.task_card(task_name))).to_be_visible(timeout=10000)
    project_page.delete_project(project_name)


def test_tc_5_7_assign_executor(page, login_and_create_project, test_user):
    project_page, task_page, project_name = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    project_page.open_project(project_name)
    executor_name = test_user["full_name"] 
    task_page.assign_executor(task_name, executor_name)
    card = task_page.task_card(task_name)
    expect(card).to_contain_text(test_user["full_name"][2])
    project_page.delete_project(project_name)


def test_tc_5_8_add_checklist(page, login_and_create_project):
    project_page, task_page, project_name = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    project_page.open_project(project_name)
    items = ["Пункт 1", "Пункт 2"]
    task_page.add_checklist_items(task_name, items)
    expect(page.get_by_text("Пункт 1")).to_be_visible()
    expect(page.get_by_text("Пункт 2")).to_be_visible()
    page.get_by_test_id("closeButton").click()
    project_page.delete_project(project_name)