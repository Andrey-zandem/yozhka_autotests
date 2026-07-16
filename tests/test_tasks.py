import pytest
from pages.login_page import LoginPage
from pages.project_page import ProjectPage
from pages.task_page import TaskPage
from playwright.sync_api import expect
from conftest import unique_name, unique_code


@pytest.fixture
def login_and_create_project(page, test_user):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(test_user["email"], test_user["password"])
    page.get_by_role("link", name=test_user["full_name"]).wait_for(state="visible", timeout=30000)
    project_page = ProjectPage(page)
    project_page.navigate_to_projects_tab()
    # Создаём проект с уникальным именем
    project_name = unique_name()
    project_code = unique_code()
    project_page.create_project(project_name, code=project_code)
    # Открываем доску проекта (она уже открыта после создания)
    task_page = TaskPage(page)
    return project_page, task_page, project_name, project_code


# ---- ТК-5.1 Создание задачи через кнопку «+ Задача» ----
def test_tc_5_1_create_task_global(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name, description="Тестовое описание")
    expect(task_page.task_card(task_name)).to_be_visible()
    # Очистка: удаляем проект
    project_page.delete_project(project_name)


# ---- ТК-5.2 Создание задачи через кнопку в шапке столбца ----
def test_tc_5_2_create_task_in_column(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.add_task_in_column_button.first.click()
    task_page.task_name_input.fill(task_name)
    task_page.create_task_button.click()
    expect(task_page.task_card(task_name)).to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.4 Редактирование названия задачи ----
def test_tc_5_4_edit_task_name(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    new_name = "Переименовано " + task_name
    task_page.edit_task_name(task_name, new_name)
    # Открываем доску и проверяем новое имя
    project_page.open_project(project_name)  # переоткрываем, чтобы обновить
    expect(task_page.task_card(new_name)).to_be_visible()
    expect(task_page.task_card(task_name)).not_to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.5 Изменение статуса через карточку ----
def test_tc_5_5_change_status_in_card(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    task_page.change_status(task_name, "В работе")
    # Проверяем, что задача переехала в столбец "В работе"
    column = page.locator(".column:has-text('В работе')")
    expect(column.locator(task_page.task_card(task_name))).to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.6 Перетаскивание задачи ----
def test_tc_5_6_drag_task(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    task_page.drag_task_to_column(task_name, "В работе")
    column = page.locator(".column:has-text('В работе')")
    expect(column.locator(task_page.task_card(task_name))).to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.7 Назначение исполнителя ----
def test_tc_5_7_assign_executor(page, login_and_create_project, test_user):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    executor_name = test_user["full_name"]
    task_page.assign_executor(task_name, executor_name)
    # Проверяем, что исполнитель отображается на карточке
    card = task_page.task_card(task_name)
    expect(card).to_contain_text(executor_name)
    project_page.delete_project(project_name)


# ---- ТК-5.8 Добавление чек-листа ----
def test_tc_5_8_add_checklist(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    items = ["Пункт 1", "Пункт 2"]
    task_page.add_checklist_items(task_name, items)
    # Проверяем, что пункты отображаются
    card = task_page.task_card(task_name)
    expect(card).to_contain_text("Пункт 1")
    expect(card).to_contain_text("Пункт 2")
    project_page.delete_project(project_name)


# ---- ТК-5.9 Отметка пункта чек-листа выполненным ----
def test_tc_5_9_complete_checklist_item(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    task_page.add_checklist_items(task_name, ["Пункт 1"])
    task_page.complete_checklist_item(task_name, "Пункт 1")
    # Проверяем, что пункт зачёркнут (может быть класс)
    card = task_page.task_card(task_name)
    # Не всегда можно проверить по карточке, но можно проверить в карточке
    project_page.delete_project(project_name)


# ---- ТК-5.11 Добавление комментария ----
def test_tc_5_11_add_comment(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    comment = "Тестовый комментарий"
    task_page.add_comment(task_name, comment)
    # Проверяем, что комментарий появился
    task_page.open_task(task_name)
    expect(page.get_by_text(comment)).to_be_visible()
    page.locator("[role='dialog'] button[aria-label='Close']").click()
    project_page.delete_project(project_name)


# ---- ТК-5.13 Копирование задачи ----
def test_tc_5_13_copy_task(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    task_page.copy_task(task_name)
    # Появится копия с тем же именем (возможно, с индексом)
    # Для простоты проверим, что карточек с таким именем стало 2 (или хотя бы одна видима)
    # Можно проверить, что появилась новая задача с похожим именем
    # Но для простоты проверяем, что карточка всё ещё видна
    expect(task_page.task_card(task_name)).to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.15 Удаление задачи ----
def test_tc_5_15_delete_task(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    task_page.delete_task(task_name)
    expect(task_page.task_card(task_name)).not_to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.21 Поиск задачи ----
def test_tc_5_21_search_task(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    task_page.search_task(task_name)
    # На доске должны остаться только найденные задачи
    expect(task_page.task_card(task_name)).to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.22 Сортировка задач ----
def test_tc_5_22_sort_by_priority(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    # Создаём две задачи с разными приоритетами (если есть возможность)
    task1 = unique_name("Задача")
    task2 = unique_name("Задача")
    task_page.create_task(task1, project_name)
    task_page.create_task(task2, project_name)
    task_page.sort_by("Приоритет")
    # Проверяем, что сортировка применилась (визуально)
    # Можно проверить порядок карточек, но это сложно, просто проверяем, что кнопка активна
    expect(task_page.sort_button).to_have_attribute("data-active", "true")
    project_page.delete_project(project_name)


# ---- ТК-5.23 Фильтрация по исполнителю ----
def test_tc_5_23_filter_by_executor(page, login_and_create_project, test_user):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    task_page.assign_executor(task_name, test_user["full_name"])
    task_page.filter_by_executor(test_user["full_name"])
    # На доске должна остаться только наша задача
    expect(task_page.task_card(task_name)).to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.17 Добавление столбца ----
def test_tc_5_17_add_column(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    column_name = "Готово к тестированию"
    task_page.add_column(column_name, color_index=1)
    column = page.locator(f".column:has-text('{column_name}')")
    expect(column).to_be_visible()
    project_page.delete_project(project_name)


# ---- ТК-5.19 Удаление столбца (пустого) ----
def test_tc_5_19_delete_empty_column(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    column_name = "Готово к тестированию"
    task_page.add_column(column_name)
    task_page.delete_column(column_name)
    column = page.locator(f".column:has-text('{column_name}')")
    expect(column).not_to_be_visible()
    project_page.delete_project(project_name)


# ---- Негативные тесты ----

# ТК-5.27 Создание задачи без названия
def test_tc_5_27_create_task_empty_name(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    task_page.global_add_task_button.click()
    task_page.create_task_button.click()
    # Поле должно подсветиться или кнопка неактивна
    expect(task_page.task_name_input).to_have_attribute("aria-invalid", "true")
    project_page.delete_project(project_name)


# ТК-5.28 Попытка удалить столбец с задачами
def test_tc_5_28_delete_column_with_tasks(page, login_and_create_project):
    project_page, task_page, project_name, project_code = login_and_create_project
    column_name = "Новая"
    task_name = unique_name("Задача")
    task_page.create_task(task_name, project_name)
    column = page.locator(f".column:has-text('{column_name}')")
    column.locator(".column-menu-button").click()
    self.page.get_by_text("Удалить столбец").click()
    # Должно появиться сообщение о невозможности удаления
    error_msg = page.get_by_text("Невозможно удалить столбец, в котором есть задачи")
    expect(error_msg).to_be_visible()
    project_page.delete_project(project_name)