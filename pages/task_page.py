import re
from datetime import datetime
from playwright.sync_api import Page, expect


class TaskPage:
    def __init__(self, page: Page):
        self.page = page

        self.global_add_task_button = page.get_by_role("button", name="Задача")
        self.add_task_in_column_button = page.locator("#column_head_1").get_by_role("button", name="Создать задачу")

        self.project_selector = page.get_by_text("Выбери проект")
        self.task_name_input = page.get_by_role("textbox", name="Назови задачу")
        self.project_select = page.get_by_role("dialog").get_by_text("Тестовый проект")
        self.create_task_button = page.get_by_role("dialog").get_by_role("button", name="Создать")
        self.task_description_input = page.get_by_role("textbox", name="Опиши задачу")
        self.create_task_button_for_col = page.locator("#column_head_1").get_by_role("button", name="Создать задачу")
        
        self.task_more_button = page.get_by_test_id("iconButton")
        self.copy_option = page.get_by_text("Создать копию", exact=True)
        self.move_option = page.get_by_text("Переместить задачу", exact=True)
        self.delete_option = page.get_by_text("Удалить задачу", exact=True)

        self.add_checklist_item_button = page.get_by_role("button", name="Добавить пункт")
        self.checklist_item_input = page.locator(".tiptap").first

        self.comment_input = page.locator(".comment-input .tiptap")
        self.submit_comment_button = page.get_by_role("button", name="⌘/Ctrl + Enter для отправки")

        self.attach_button = page.locator("#commentsTabFormBlock").get_by_test_id("iconButton")

        self.search_button = page.get_by_role("button", name="Поиск")
        self.search_input = page.get_by_role("textbox", name="Поиск")
        self.sort_button = page.get_by_role("button", name="Сортировка")
        self.filter_button = page.get_by_role("button", name="Фильтрация")

        self.add_column_button = page.locator("._addColumnBtn_1plce_10")
        self.column_name_input = page.get_by_role("textbox")
        self.column_color_options = page.get_by_test_id("status-color")
        self.add_column_confirm = page.get_by_role("button", name="Добавить", exact=True)

        self.success_message = page.locator(".success-message")

    def get_column_by_status(self, status: str):
        """Возвращает локатор столбца по его статусу (например, 'В работе')."""
        return self.page.locator(f"div:has(span[data-testid='text']:has-text('{status}'))").first

    def create_task(self, task_name: str, project_name: str, description: str = None):
        self.global_add_task_button.wait_for(state="visible", timeout=30000)
        self.global_add_task_button.click()
        project_selector = self.page.get_by_text("Выбери проект")
        project_selector.wait_for(state="visible", timeout=10000)
        project_selector.click()
        dialog = self.page.get_by_role("dialog")
        project_item = dialog.get_by_text(project_name, exact=True).first
        project_item.wait_for(state="visible", timeout=20000)
        project_item.click()
        self.task_name_input.wait_for(state="visible", timeout=15000)
        self.task_name_input.fill(task_name)
        if description:
            self.task_description_input.wait_for(state="visible", timeout=5000)
            self.task_description_input.fill(description)
            self.page.click("body")
            self.page.wait_for_timeout(5000)
        expect(self.create_task_button).to_be_enabled(timeout=30000)
        self.create_task_button.click()
        self.task_name_input.wait_for(state="hidden", timeout=25000)
        return task_name
    
    def create_task_in_column(self, task_name: str):
        """Создаёт задачу через кнопку в шапке столбца 'Новая'."""
        self.add_task_in_column_button.click()
        self.task_name_input.fill(task_name)
        self.create_task_button_for_col.click()
        self.task_name_input.wait_for(state="hidden", timeout=10000)

    def create_task_in_all_tasks(self, task_name: str, project_name: str):
        """Создаёт задачу через раздел 'Все задачи' (межпроектная доска)."""
        self.page.get_by_role("link", name="Все задачи").click()
        self.page.wait_for_selector("[data-rbd-droppable-id]", state="visible", timeout=10000)
        today = datetime.now().strftime("%d.%m.%Y")
        day_container = self.page.locator(f"[data-rbd-droppable-id='{today}']")
        if day_container.count() == 0:
            day_container = self.page.locator("[data-rbd-droppable-id]").first
        day_container.hover()
        create_button = day_container.get_by_role("button", name="Создать задачу")
        create_button.wait_for(state="visible", timeout=5000)
        create_button.click()
        dialog = self.page.get_by_role("dialog")
        project_item = dialog.get_by_text(project_name, exact=True).first
        self.page.get_by_text("Выбери проект").wait_for(state="visible", timeout=500)
        self.page.get_by_text("Выбери проект").click()
        project_item.wait_for(state="visible", timeout=20000)
        project_item.click()
        self.task_name_input.fill(task_name)
        self.create_task_button.click()
        self.task_name_input.wait_for(state="hidden", timeout=10000)
        
    def open_task(self, task_name: str):
        card = self.task_card(task_name)
        card.wait_for(state="visible", timeout=30000)
        card.click(force=True)
        dialog = self.page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=40000)
        # Проверяем, что внутри модалки есть название задачи
        dialog.get_by_text(task_name).wait_for(state="visible", timeout=30000)
        return dialog

    def edit_task_name(self, task_name: str, new_name: str):
        self.open_task(task_name)
        self.page.get_by_test_id("modal-container").get_by_text(task_name).click()
        self.task_name_input.fill(new_name)
        self.page.click("body")
        self.page.get_by_test_id("closeButton").click()
        self.page.reload()
        self.task_card(new_name).wait_for(state="visible", timeout=10000)

    def change_status(self, task_name: str, new_status: str):
        dialog = self.open_task(task_name)
        status_button = dialog.get_by_role("button").filter(has_text=re.compile(r"^(Новая|В работе|Закрыта|В ожидании)$")).first
        status_button.click()
        dropdown = self.page.locator("div._content_j87nf_15")
        dropdown.wait_for(state="visible", timeout=5000)
        dropdown.locator(f"span[data-testid='text']:has-text('{new_status}')").click()
        dialog.get_by_test_id("closeButton").click()
        self.page.reload()
        dialog.wait_for(state="hidden", timeout=5000)

    def assign_executor(self, task_name: str, executor_name: str):
        self.open_task(task_name)
        parts = executor_name.split(maxsplit=1)
        search_text = parts[1] if len(parts) > 1 else executor_name
        self.page.get_by_role("button", name="Выбрать").first.click()
        user_list = self.page.locator("._userList_103pu_175")
        user_list.wait_for(state="visible", timeout=10000)
        target = user_list.locator(f"._title_1vusl_24:has-text('{search_text}')").first
        target.click(force=True)
        self.page.get_by_test_id("closeButton").click()
        self.page.reload()

    def add_checklist_items(self, task_name: str, items: list):
        self.open_task(task_name)
        for item in items:
            self.add_checklist_item_button.click()
            input_field = self.page.locator(".tiptap").first
            input_field.wait_for(state="visible", timeout=5000)
            input_field.fill(item)
            input_field.press("Enter")
            self.page.wait_for_timeout(5000)
        
    def task_card(self, name: str):
        """Ищет карточку задачи по частичному совпадению названия."""
        self.page.locator(f"a[href*='/board/']:has-text('{name}')").first.wait_for(state="visible", timeout=30000)
        return self.page.locator(f"a[href*='/board/']:has-text('{name}')").first
