from playwright.sync_api import Page, expect


class ProjectPage:
    def __init__(self, page: Page):
        self.page = page
        # Элементы на странице проектов (вкладка "Проекты" в пространстве)
        self.create_project_button = page.get_by_role("button", name="+ Создать проект")
        # Окно создания проекта
        self.project_name_input = page.get_by_role("textbox", name="Название проекта")
        self.project_code_input = page.get_by_role("textbox", name="Код проекта")
        self.create_button = page.get_by_role("button", name="Создать")
        self.save_button = page.get_by_role("button", name="Сохранить")
        # Элементы на доске проекта
        self.project_title = page.locator(".project-title")
        self.project_icon = page.locator(".project-icon-button")
        self.rename_option = page.get_by_text("Переименовать проект")
        self.archive_option = page.get_by_text("Архивировать")
        self.delete_option = page.get_by_text("Удалить")
        self.restore_option = page.get_by_text("Восстановить из архива")
        self.favorite_option = page.get_by_text("Добавить в избранное")
        self.unfavorite_option = page.get_by_text("Убрать из избранного")
        # Архивный блок
        self.archive_block = page.locator(".archive-block")
        self.active_projects = page.locator(".active-projects")
        # Сообщения об успехе/ошибке
        self.success_message = page.locator(".success-message")
        self.error_message = page.locator(".error-message")

    def navigate_to_projects_tab(self):
        """Переход на вкладку 'Проекты' в пространстве (если не активна)"""
        self.page.get_by_role("link", name="О пространстве").click()
        self.page.get_by_role("button", name="Проекты").click()

    def open_create_project_modal(self):
        """Открыть модалку создания проекта"""
        self.create_project_button.click()
        # Ждём загрузки окна
        self.project_name_input.wait_for(state="visible", timeout=30000)

    def create_project(self, name: str, code: str = None):
        """Создать проект с указанным названием и кодом"""
        self.open_create_project_modal()
        self.project_name_input.fill(name)
        if code:
            self.project_code_input.fill(code)
        self.create_button.click()
        # Ждём, пока проект создастся (появится сообщение или доска)
        self.page.wait_for_timeout(2000)  

    def get_project_item(self, project_name: str):
        """Вернуть элемент проекта в меню навигации или на вкладке"""
        return self.page.locator(f".project-item:has-text('{project_name}')")

    def open_project(self, project_name: str):
        """Открыть проект по имени (клик по названию в меню)"""
        self.get_project_item(project_name).click()

    def open_project_menu(self, project_name: str):
        """Открыть контекстное меню проекта (три точки)"""
        project = self.get_project_item(project_name)
        project.hover()
        project.locator(".project-more-button").click()

    def rename_project(self, project_name: str, new_name: str):
        """Переименовать проект"""
        self.open_project_menu(project_name)
        self.rename_option.click()
        self.project_name_input.fill(new_name)
        self.save_button.click()

    def archive_project(self, project_name: str, code: str):
        """Архивировать проект (требуется ввод кода)"""
        self.open_project_menu(project_name)
        self.archive_option.click()
        # Вводим код в диалоге подтверждения
        confirm_input = self.page.get_by_role("textbox")
        confirm_input.fill(code)
        self.page.get_by_role("button", name="Архивировать").click()

    def restore_project(self, project_name: str):
        """Восстановить проект из архива"""
        self.navigate_to_projects_tab()
        # Находим проект в архиве
        archived_project = self.archive_block.locator(f".project-card:has-text('{project_name}')")
        archived_project.hover()
        archived_project.locator(".project-more-button").click()
        self.restore_option.click()
        self.page.get_by_role("button", name="Восстановить").click()

    def delete_project(self, project_name: str, code: str):
        """Удалить проект (требуется ввод кода)"""
        self.open_project_menu(project_name)
        self.delete_option.click()
        confirm_input = self.page.get_by_role("textbox")
        confirm_input.fill(code)
        self.page.get_by_role("button", name="Удалить").click()

    def add_to_favorites(self, project_name: str):
        """Добавить проект в избранное"""
        self.open_project_menu(project_name)
        self.favorite_option.click()

    def remove_from_favorites(self, project_name: str):
        """Убрать проект из избранного"""
        self.open_project_menu(project_name)
        self.unfavorite_option.click()

    def check_success_message(self, expected_text: str = "Проект успешно создан"):
        """Проверить сообщение об успехе"""
        expect(self.success_message).to_contain_text(expected_text)

    def check_error_message(self, expected_text: str):
        """Проверить сообщение об ошибке"""
        expect(self.error_message).to_contain_text(expected_text)