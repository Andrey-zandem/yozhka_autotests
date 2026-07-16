import re
from playwright.sync_api import Page, expect

class TaskPage:
    def __init__(self, page: Page):
        self.page = page

        # ---- Кнопки создания задачи ----
        self.global_add_task_button = page.get_by_role("button", name="Создать задачу")
        self.add_task_in_column_button = page.locator(".column-header .add-task-button")

        # ---- Модалка создания задачи ----
        self.task_name_input = page.get_by_role("textbox", name="Назови задачу")
        self.project_select = page.get_by_role("dialog").get_by_text("Тестовый проект")  # будет заменяться
        self.create_task_button = page.get_by_role("button", name="Создать", exact=True)
        self.task_description_input = page.locator(".task-description textarea")

        # ---- Карточка задачи (по названию) ----
        def task_card(name: str):
            return page.get_by_role("button", name=name)

        # ---- Контекстное меню в карточке (три точки) ----
        self.task_more_button = page.get_by_test_id("iconButton")
        self.copy_option = page.get_by_text("Создать копию", exact=True)
        self.move_option = page.get_by_text("Переместить задачу", exact=True)
        self.delete_option = page.get_by_text("Удалить задачу", exact=True)

        # ---- Чек-лист ----
        self.add_checklist_item_button = page.get_by_role("button", name="Добавить пункт")
        self.checklist_item_input = page.locator(".tiptap").first

        # ---- Комментарии ----
        self.comment_input = page.locator(".comment-input .tiptap")
        self.submit_comment_button = page.get_by_role("button", name="⌘/Ctrl + Enter для отправки")

        # ---- Вложения ----
        self.attach_button = page.locator("#commentsTabFormBlock").get_by_test_id("iconButton")

        # ---- Поиск, сортировка, фильтрация ----
        self.search_button = page.get_by_role("button", name="Поиск")
        self.search_input = page.get_by_role("textbox", name="Поиск")
        self.sort_button = page.get_by_role("button", name="Сортировка")
        self.filter_button = page.get_by_role("button", name="Фильтрация")

        # ---- Столбцы на доске ----
        self.add_column_button = page.locator("._addColumnBtn_1plce_10")
        self.column_name_input = page.get_by_role("textbox")
        self.column_color_options = page.get_by_test_id("status-color")
        self.add_column_confirm = page.get_by_role("button", name="Добавить", exact=True)

        # ---- Успешные сообщения ----
        self.success_message = page.locator(".success-message")

    # ---- Создание задачи ----
    def create_task(self, task_name: str, project_name: str = None, description: str = None):
        self.global_add_task_button.click()
        if project_name:
            self.page.get_by_role("dialog").get_by_text(project_name).click()
        self.task_name_input.fill(task_name)
        if description:
            self.task_description_input.fill(description)
        self.create_task_button.click()
        # Ждём появления карточки на доске
        self.task_card(task_name).wait_for(state="visible", timeout=10000)
        return task_name

    # ---- Открыть карточку задачи ----
    def open_task(self, task_name: str):
        self.task_card(task_name).click()

    # ---- Редактировать название ----
    def edit_task_name(self, task_name: str, new_name: str):
        self.open_task(task_name)
        self.page.get_by_test_id("modal-container").get_by_text(task_name).click()
        self.task_name_input.fill(new_name)
        self.page.click("body")  # снять фокус
        # Закрыть карточку (по клику вне или по крестику)
        self.page.locator("[role='dialog'] button[aria-label='Close']").click()

    # ---- Изменить статус через карточку ----
    def change_status(self, task_name: str, new_status: str):
        self.open_task(task_name)
        status_button = self.page.get_by_role("button", name=task_name)
        status_button.click()  # открывает выпадающий список
        self.page.get_by_role("button", name=new_status).click()
        # Закрыть карточку
        self.page.locator("[role='dialog'] button[aria-label='Close']").click()

    # ---- Перетаскивание задачи ----
    def drag_task_to_column(self, task_name: str, column_name: str):
        task = self.task_card(task_name)
        column = self.page.locator(f".column:has-text('{column_name}')")
        task.drag_to(column)

    # ---- Назначить исполнителя ----
    def assign_executor(self, task_name: str, executor_name: str):
        self.open_task(task_name)
        self.page.get_by_role("button", name="Выбрать").first.click()
        self.page.get_by_text(executor_name).click()
        self.page.locator("[role='dialog'] button[aria-label='Close']").click()

    # ---- Добавить чек-лист ----
    def add_checklist_items(self, task_name: str, items: list):
        self.open_task(task_name)
        for item in items:
            self.add_checklist_item_button.click()
            self.checklist_item_input.fill(item)
            self.checklist_item_input.press("Enter")
        self.page.locator("[role='dialog'] button[aria-label='Close']").click()

    # ---- Отметить пункт чек-листа выполненным ----
    def complete_checklist_item(self, task_name: str, item_text: str):
        self.open_task(task_name)
        item_checkbox = self.page.locator(f".checklist-item:has-text('{item_text}') .checkbox")
        item_checkbox.click()
        self.page.locator("[role='dialog'] button[aria-label='Close']").click()

    # ---- Добавить комментарий ----
    def add_comment(self, task_name: str, comment: str):
        self.open_task(task_name)
        self.comment_input.fill(comment)
        self.submit_comment_button.click()
        self.page.locator("[role='dialog'] button[aria-label='Close']").click()

    # ---- Копировать задачу ----
    def copy_task(self, task_name: str, target_project: str = None):
        self.open_task(task_name)
        self.task_more_button.click()
        self.copy_option.click()
        if target_project:
            self.page.select_option("#projectCopy", target_project)
        self.page.get_by_role("button", name="Создать копию").click()
        self.page.locator("[role='dialog'] button[aria-label='Close']").click()

    # ---- Переместить задачу (только владелец/админ) ----
    def move_task(self, task_name: str, target_project: str):
        self.open_task(task_name)
        self.task_more_button.click()
        self.move_option.click()
        self.page.select_option("#projectMove", target_project)
        self.page.get_by_role("button", name="Переместить").click()
        self.page.locator("[role='dialog'] button[aria-label='Close']").click()

    # ---- Удалить задачу ----
    def delete_task(self, task_name: str):
        self.open_task(task_name)
        self.task_more_button.click()
        self.delete_option.click()
        self.page.get_by_role("button", name="Удалить", exact=True).click()
        # Ждём, пока карточка исчезнет с доски
        self.task_card(task_name).wait_for(state="detached", timeout=10000)

    # ---- Поиск задачи ----
    def search_task(self, query: str):
        self.search_button.click()
        self.search_input.fill(query)
        self.search_input.press("Enter")

    # ---- Сортировка ----
    def sort_by(self, criteria: str):
        self.sort_button.click()
        self.page.get_by_role("button", name=criteria).click()

    # ---- Фильтрация по исполнителю ----
    def filter_by_executor(self, executor_name: str):
        self.filter_button.click()
        self.page.get_by_role("button", name="Исполнитель").click()
        self.page.get_by_text(executor_name).click()

    # ---- Добавить столбец (владелец/админ) ----
    def add_column(self, column_name: str, color_index: int = 1):
        self.add_column_button.click()
        self.column_name_input.fill(column_name)
        self.column_color_options.nth(color_index).click()
        self.add_column_confirm.click()
        # Ждём появления нового столбца
        self.page.locator(f".column:has-text('{column_name}')").wait_for(state="visible", timeout=10000)

    # ---- Удалить столбец (владелец/админ) ----
    def delete_column(self, column_name: str):
        column = self.page.locator(f".column:has-text('{column_name}')")
        column.locator(".column-menu-button").click()
        self.page.get_by_text("Удалить столбец").click()
        self.page.get_by_role("button", name="Удалить", exact=True).click()
        column.wait_for(state="detached", timeout=10000)

    # ---- Вспомогательные методы ----
    def task_card(self, name: str):
        return self.page.get_by_role("button", name=name)