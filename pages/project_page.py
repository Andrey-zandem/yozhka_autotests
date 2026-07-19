import re
from playwright.sync_api import Page, expect


class ProjectPage:
    def __init__(self, page: Page):
        self.page = page

        # --- Верхний уровень / список проектов ---
        self.create_project_button = page.get_by_role(
            "button", name=re.compile(r"Создать проект", re.IGNORECASE)
        )
        self.project_name_input = page.get_by_role("textbox", name="Название проекта")
        self.project_code_input = page.get_by_role("textbox", name="Код пространства")
        self.open_code_field_button = page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(3)

        self.create_button = page.get_by_role("button", name="Создать", exact=True)
        self.save_button = page.get_by_role("button", name="Сохранить")

        # --- Переименование / смена иконки (ТК-3.2, ТК-3.3) ---
        self.board_header = page.locator("div._head_xn6fh_10")
        self.project_icon_button = self.board_header.get_by_test_id("avatar")
        self.rename_input = page.get_by_role("textbox")

        self.archive_block = page.locator("._sectionContent_1wkit_93")

        # --- Меню проекта в навигации (три точки у элемента списка) ---
        self.board_more_button = page.get_by_test_id("iconButton")

        self.favorites_heading = page.get_by_text("Избранные", exact=False)
        self.active_heading = page.get_by_text("Активные", exact=False).first
        self.archive_heading = page.get_by_text("Архив", exact=False).first
 
    # Навигация
    def navigate_to_projects_tab(self):
        # Если уже на странице проектов — выходим
        if "/projects" in self.page.url:
            return
        # Кликаем по ссылке "О пространстве"
        self.page.get_by_role("link", name="О пространстве").click()
        # Ждём появления вкладки "Проекты" и кликаем
        projects_tab = self.page.get_by_role("button", name="Проекты")
        projects_tab.wait_for(state="visible", timeout=40000)
        projects_tab.click(force=True)
        # Ждём смены URL
        self.page.wait_for_url(re.compile(r".*/projects"), timeout=30000)
        # Небольшая пауза для стабилизации
        self.page.wait_for_timeout(500)

    def open_create_project_modal(self):
        self.create_project_button.wait_for(state="visible", timeout=15000)
        self.create_project_button.click()
        self.project_name_input.wait_for(state="visible", timeout=30000)

    def get_project_link_by_code(self, code: str):
        """Возвращает ссылку на проект по его коду (часть URL)."""
        return self.page.locator(f"a[href*='/project/{code}']").first

    def get_project_link(self, name: str):
        """Ссылка на проект по частичному совпадению с именем (в меню навигации)."""
        return self.page.get_by_role("link").filter(has_text=name).first

    def open_project(self, code: str):
        """Переход на доску проекта."""
        project_link = self.get_project_link(code)
        project_link.wait_for(state="visible", timeout=30000)
        project_link.click()
        self.page.wait_for_url(re.compile(r".*/project/.*"), timeout=30000)
        self.page.get_by_text("Канбан", exact=False).wait_for(state="visible", timeout=10000)

    def get_project_code_from_url(self):
        """Извлекает код проекта из текущего URL (например, /project/PR17841081)."""
        url = self.page.url
        match = re.search(r"/project/([^/?]+)", url)
        if match:
            return match.group(1)
        raise ValueError(f"Не удалось извлечь код проекта из URL: {url}")

    def _link_in_archive(self, code: str):
        """
        Ссылка на архивный проект. 
        """
        return self.archive_heading.locator(f"xpath=following::a[contains(@href, '/project/{code}')]").first

    def _link_in_favorites(self, name: str):
        """
        Ссылка на проект в блоке "Избранные". 
        """
        candidates = self.favorites_heading.locator(
            "xpath=following::a[contains(@href, '/project/')]"
            "[following::*[contains(normalize-space(.), 'Активные')]]"
        )
        return candidates.filter(has_text=name).first

    def open_board_menu(self, name: str):
        """
        Открывает контекстное меню проекта (три точки) через наведение на
        элемент проекта в меню навигации.
        """
        project_link = self.get_project_link(name)
        project_link.hover()
        more_button = project_link.get_by_test_id("iconButton")
        more_button.wait_for(state="visible", timeout=30000)
        more_button.click()

    # ТК-3.1 Создание проекта
    def create_project(self, name: str) -> str:
        self.open_create_project_modal()
        self.project_name_input.fill(name)
        self.page.click("body")
        self.create_button.click()
        self.project_name_input.wait_for(state="hidden", timeout=30000)
        self.open_project(name)
        # Извлекаем код из URL
        url = self.page.url
        code = url.split("/project/")[1].split("/")[0]
        return code

    # ТК-3.2 Переименование проекта
    def rename_project(self, new_name: str):
        """Вызывать, находясь на доске проекта."""
        self.project_icon_button.click()
        self.page.get_by_text("Переименовать проект", exact=True).click()
        self.rename_input.fill(new_name)
        self.save_button.click()

    # ТК-3.3 Смена иконки проекта
    def change_icon(self, name: str):
        """
        Изменяет иконку проекта на кошачью лапку
        """
        self.open_project(name)
        # Открываем меню изменения иконки
        self.page.locator("._head_xn6fh_10 [data-testid='avatar']").click()
        self.page.get_by_text("Изменить иконку").click()
        self.page.locator("#solid_p_paw > ._icon_1dmpy_27 > use").click()
        self.page.get_by_role("button", name="Сохранить").click()

    # ТК-3.4 Архивирование проекта
    def archive_project(self, name: str):
        self.open_project(name)
        code = self.get_project_code_from_url()
        self.open_board_menu(name)
        self.page.get_by_text("Архивировать").click()
        confirm_input = self.page.get_by_role("textbox")
        confirm_input.fill(code)
        self.page.get_by_role("button", name="Архивировать").click()
        expect(self.get_project_link(name)).not_to_be_visible(timeout=30000)
        self.navigate_to_projects_tab()
        expect(self._link_in_archive(code)).to_be_visible(timeout=10000)

    # ТК-3.5 Восстановление проекта из архива
    def restore_project(self, name: str):
        """Восстанавливает проект из архива по его имени."""
        self.navigate_to_projects_tab()
        archived_card = self.archive_block.locator(f"._card_1wkit_97:has-text('{name}')").first
        archived_card.wait_for(state="visible", timeout=10000)
        archived_card.hover()
        more_button = archived_card.get_by_test_id("iconButton")
        more_button.wait_for(state="visible", timeout=10000)
        more_button.click()
        self.page.get_by_text("Восстановить из архива").click()
        self.page.get_by_role("button", name="Восстановить").click()
        expect(self.get_project_link(name)).to_be_visible(timeout=10000)

    # ТК-3.6 Удаление проекта
    def delete_project(self, name: str):
        self.open_project(name)
        code = self.get_project_code_from_url()
        self.open_board_menu(name)
        delete_item = self.page.get_by_text("Удалить")
        delete_item.click()
        self.page.get_by_text("Удалить проект").wait_for(state="visible", timeout=10000)
        confirm_input = self.page.get_by_role("textbox").first
        confirm_input.fill(code)
        delete_button = self.page.get_by_role("button", name="Удалить")
        expect(delete_button).to_be_enabled(timeout=10000)
        delete_button.click()
        confirm_input.wait_for(state="hidden", timeout=30000)
        self.navigate_to_projects_tab()
        self.page.reload()
        # Проверяем, что проект с данным кодом больше не отображается в меню
        expect(self.get_project_link_by_code(code)).not_to_be_visible(timeout=10000)

    # ТК-3.7 / ТК-3.8 Избранное
    def add_to_favorites(self, name: str):
        self.open_project(name)
        self.open_board_menu(name)
        menu_item = self.page.get_by_text("Добавить в избранное", exact=True)
        menu_item.click()
        menu_item.wait_for(state="hidden", timeout=5000)
        self.navigate_to_projects_tab()
        self.favorites_heading.wait_for(state="visible", timeout=20000)
        expect(self._link_in_favorites(name)).to_be_visible(timeout=20000)

    def remove_from_favorites(self, name: str):
        self.open_project(name)
        self.open_board_menu(name)
        self.page.get_by_text("Убрать из избранного").click()
        self.navigate_to_projects_tab()
        expect(self._link_in_favorites(name)).not_to_be_visible(timeout=20000)

    # Общее
    def check_error_message(self, expected_text: str):
        expect(self.page.get_by_text(expected_text)).to_be_visible()