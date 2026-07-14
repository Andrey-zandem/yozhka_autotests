# import re
# from playwright.sync_api import Page, expect

# class ProjectPage:
#     def __init__(self, page: Page):
#         self.page = page
#         self.create_project_button = page.get_by_role("button", name=re.compile(r"Создать проект", re.IGNORECASE))
#         self.project_name_input = page.get_by_role("textbox", name="Название проекта")
#         self.open_code_field_button = page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(3)
#         self.project_code_input = page.get_by_role("textbox", name="Код пространства")
#         self.create_button = page.get_by_role("button", name="Создать", exact=True)
#         self.save_button = page.get_by_role("button", name="Сохранить")
#         self.board_more_button = page.get_by_test_id("iconButton")  
#         self.archive_block = page.locator(".archive-block")
#         self.favorites_block = page.locator(".favorites-block")

#     def navigate_to_projects_tab(self):
#         if "/projects" not in self.page.url:
#             self.page.get_by_role("link", name="О пространстве").click()
#             self.page.get_by_role("button", name="Проекты").click()
#         self.create_project_button.wait_for(state="visible", timeout=30000)

#     def open_create_project_modal(self):
#         self.create_project_button.click()
#         self.project_name_input.wait_for(state="visible", timeout=30000)

#     def get_project_link(self, name: str):
#         """Возвращает ссылку на проект по частичному совпадению с именем"""
#         return self.page.get_by_role("link").filter(has_text=name).first

#     def open_project(self, name: str):
#         """Переход на доску проекта"""
#         project_link = self.get_project_link(name)
#         project_link.wait_for(state="visible", timeout=30000)
#         project_link.click()
#         self.page.wait_for_url(re.compile(r".*/board$"), timeout=10000)

#     def open_board_menu(self, name: str):
#         """Открывает меню проекта через три точки (наведение и клик)"""
#         project_link = self.get_project_link(name)
#         project_link.hover()  # наводим курсор, чтобы появилась кнопка
#         more_button = project_link.get_by_test_id("iconButton")
#         more_button.wait_for(state="visible", timeout=30000)
#         more_button.click()
#         self.page.wait_for_timeout(500)

#     def create_project(self, name: str, code: str = None):
#         self.open_create_project_modal()
#         self.project_name_input.fill(name)
#         self.page.click("body")
#         if code:
#             self.open_code_field_button.wait_for(state="visible", timeout=30000)
#             self.open_code_field_button.click()
#             self.project_code_input.wait_for(state="visible", timeout=30000)
#             self.project_code_input.fill(code)
#             self.page.click("body")
#         self.create_button.click()
#         self.page.locator("[role='dialog']").wait_for(state="hidden", timeout=30000)
#         # Переходим на доску проекта
#         self.open_project(name)

#     def archive_project(self, name: str, code: str):
#         self.open_project(name)
#         self.open_board_menu()
#         self.page.get_by_text("Архивировать", exact=True).click()
#         confirm_input = self.page.get_by_role("textbox")
#         confirm_input.fill(code)
#         self.page.get_by_role("button", name="Архивировать", exact=True).click()
#         self.navigate_to_projects_tab()
#         # Проверяем, что проект появился в блоке "Архив"
#         archive_heading = self.page.get_by_text("Архив").first
#         archive_heading.wait_for(state="visible", timeout=20000)
#         project_in_archive = self.page.locator("div:has-text('Архив')").locator(f"a:has-text('{name}')").first
#         expect(project_in_archive).to_be_visible(timeout=10000)

#     def restore_project(self, name: str):
#         self.navigate_to_projects_tab()
#         archived = self.archive_block.locator(f".project-card:has-text('{name}')").first
#         archived.hover()
#         more_button = archived.get_by_test_id("iconButton")
#         more_button.click()
#         self.page.get_by_text("Восстановить из архива", exact=True).click()
#         self.page.get_by_role("button", name="Восстановить").click()
#         expect(self.get_project_link(name)).to_be_visible(timeout=10000)

#     def delete_project(self, name: str, code: str):
#         self.open_project(name)
#         self.open_board_menu(name)
#         self.page.get_by_text("Удалить").click()
#         confirm_input = self.page.get_by_role("textbox")
#         confirm_input.fill(code)
#         self.page.get_by_role("button", name="Удалить").click()
#         self.navigate_to_projects_tab()
#         expect(self.get_project_link(name)).not_to_be_visible(timeout=10000)

#     def add_to_favorites(self, name: str):
#         self.open_project(name)
#         self.open_board_menu(name)
#         self.page.get_by_text("Добавить в избранное", exact=True).click()
#         self.navigate_to_projects_tab()
#         # Ждём появления блока избранных (по заголовку)
#         favorites_heading = self.page.get_by_text("Избранные").first
#         favorites_heading.wait_for(state="visible", timeout=20000)
#         # Ищем ссылку на проект внутри этого блока
#         project_in_favorites = self.page.locator("div:has-text('Избранные')").locator(f"a:has-text('{name}')").first
#         expect(project_in_favorites).to_be_visible(timeout=10000)

#     def remove_from_favorites(self, name: str):
#         self.open_project(name)
#         self.open_board_menu(name)
#         self.page.get_by_text("Убрать из избранного", exact=True).click()
#         self.navigate_to_projects_tab()
#         project_in_favorites = self.page.locator(f"a:has-text('{name}')")
#         expect(project_in_favorites).not_to_be_visible(timeout=20000)

#     def check_error_message(self, expected_text: str):
#         expect(self.page.get_by_text(expected_text)).to_be_visible()



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

        # TODO: локатор кнопки "раскрыть поле кода" собран по позиции (nth(3)),
        # это хрупко и стало причиной падения ТК-3.5 (см. отчёт по багам).
        # Как только будет доступна разметка приложения - заменить на
        # get_by_test_id(...) или get_by_role(..., name="Изменить код") и т.п.
        self.open_code_field_button = (
            page.get_by_role("button").filter(has_text=re.compile(r"^$")).nth(3)
        )
        self.project_code_input = page.get_by_role("textbox", name="Код пространства")

        self.create_button = page.get_by_role("button", name="Создать", exact=True)
        self.save_button = page.get_by_role("button", name="Сохранить")

        # --- Переименование / смена иконки (ТК-3.2, ТК-3.3) ---
        # Подтверждено реальной разметкой пользователя. Раньше брали просто
        # .first по data-testid="avatar" на всей странице — но такой же
        # аватар есть и у пункта проекта в сайдбаре, и .first там попадал
        # НЕ в шапку доски, а в сайдбар (отсюда падение ТК-3.2/3.3: клик
        # проходил, но открывалось не то меню). Шапка доски — уникальный
        # для board-страницы контейнер (класс CSS-модуля, см. TODO ниже),
        # внутри него ровно один avatar — это и нужный нам.
        #
        # TODO: класс "_head_xn6fh_10" — хэш CSS-модуля, может измениться
        # при пересборке фронтенда. Если тест снова начнёт падать с
        # таймаутом на project_icon_button — переснять разметку и обновить.
        self.board_header = page.locator("div._head_xn6fh_10")
        self.project_icon_button = self.board_header.get_by_test_id("avatar")
        self.rename_input = page.get_by_role("textbox")

        # --- Меню проекта в навигации (три точки у элемента списка) ---
        self.board_more_button = page.get_by_test_id("iconButton")

        # --- Заголовки секций на вкладке "Проекты" ---
        # Секции идут в фиксированном порядке: Избранные -> Активные -> Архив
        # (подтверждено скриншотом и aria snapshot из логов). Реальных
        # CSS-классов контейнеров у меня нет, поэтому ссылки внутри секции
        # ищем через DOM-порядок относительно этих заголовков, а не по классу.
        self.favorites_heading = page.get_by_text("Избранные", exact=False).first
        self.active_heading = page.get_by_text("Активные", exact=False).first
        self.archive_heading = page.get_by_text("Архив", exact=False).first

    # ------------------------------------------------------------------ #
    # Навигация
    # ------------------------------------------------------------------ #
    def navigate_to_projects_tab(self):
        if "/projects" not in self.page.url:
            self.page.get_by_role("link", name="О пространстве").click()
            self.page.get_by_role("button", name="Проекты").click()
        self.create_project_button.wait_for(state="visible", timeout=30000)

    def open_create_project_modal(self):
        self.create_project_button.click()
        self.project_name_input.wait_for(state="visible", timeout=30000)

    def get_project_link(self, name: str):
        """Ссылка на проект по частичному совпадению с именем (в меню навигации)."""
        return self.page.get_by_role("link").filter(has_text=name).first

    def open_project(self, name: str):
        """Переход на доску проекта."""
        project_link = self.get_project_link(name)
        project_link.wait_for(state="visible", timeout=30000)
        project_link.click()
        self.page.wait_for_url(re.compile(r".*/board$"), timeout=10000)

    def _link_in_archive(self, code: str):
        """
        Ссылка на архивный проект. "Архив" — последняя секция на странице
        (после неё других секций со ссылками нет), поэтому достаточно взять
        все ссылки, идущие в DOM после заголовка "Архив". Матчим по коду
        проекта в href — это надёжнее имени, т.к. отображаемое имя может
        обрезаться многоточием в интерфейсе.
        """
        return self.archive_heading.locator(f"xpath=following::a[contains(@href, '/project/{code}')]").first

    def _link_in_favorites(self, name: str):
        """
        Ссылка на проект в блоке "Избранные". Секция идёт первой на странице,
        сразу за ней — "Активные", поэтому ограничиваем поиск ссылками между
        этими двумя заголовками (следующий узел с текстом "Активные" должен
        идти уже ПОСЛЕ найденной ссылки).
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

        ВАЖНО: name обязателен всегда, в т.ч. если мы уже находимся на доске
        этого проекта — элемент списка в сайдбаре виден на любой странице.
        Именно отсутствие name в вызове было причиной падения ТК-3.4 / ТК-3.13.
        """
        project_link = self.get_project_link(name)
        project_link.hover()
        more_button = project_link.get_by_test_id("iconButton")
        more_button.wait_for(state="visible", timeout=30000)
        more_button.click()
        self.page.wait_for_timeout(500)

    # ------------------------------------------------------------------ #
    # ТК-3.1 Создание проекта
    # ------------------------------------------------------------------ #
    def create_project(self, name: str, code: str = None):
        self.open_create_project_modal()
        self.project_name_input.fill(name)
        self.page.click("body")
        if code:
            self.open_code_field_button.wait_for(state="visible", timeout=30000)
            self.open_code_field_button.click()
            self.project_code_input.wait_for(state="visible", timeout=30000)
            self.project_code_input.fill(code)
            self.page.click("body")
        self.create_button.click()
        self.page.locator("[role='dialog']").wait_for(state="hidden", timeout=30000)
        self.open_project(name)

    # ------------------------------------------------------------------ #
    # ТК-3.2 Переименование проекта
    # ------------------------------------------------------------------ #
    def rename_project(self, new_name: str):
        """Вызывать, находясь на доске проекта."""
        self.project_icon_button.click()
        self.page.get_by_text("Переименовать проект", exact=True).click()
        self.rename_input.fill(new_name)
        self.save_button.click()

    # ------------------------------------------------------------------ #
    # ТК-3.3 Смена иконки проекта
    # ------------------------------------------------------------------ #
    def change_icon(self, color_index: int = 2):
        """Вызывать, находясь на доске проекта."""
        self.project_icon_button.click()
        self.page.get_by_text("Изменить иконку", exact=True).click()
        self.page.get_by_test_id("status-color").nth(2).click()
        self.save_button.click()

    # ------------------------------------------------------------------ #
    # ТК-3.4 Архивирование проекта
    # ------------------------------------------------------------------ #
    def archive_project(self, name: str, code: str):
        self.open_project(name)  # гарантируем, что мы на доске
        self.open_board_menu(name)
        self.page.get_by_text("Архивировать", exact=True).click()
        confirm_input = self.page.get_by_role("textbox")
        confirm_input.fill(code)
        self.page.get_by_role("button", name="Архивировать", exact=True).click()
        expect(self.get_project_link(name)).not_to_be_visible(timeout=30000)
        self.navigate_to_projects_tab()
        expect(self._link_in_archive(code)).to_be_visible(timeout=10000)

    # ------------------------------------------------------------------ #
    # ТК-3.5 Восстановление проекта из архива
    # ------------------------------------------------------------------ #
    def restore_project(self, name: str, code: str):
        self.navigate_to_projects_tab()
        archived_link = self._link_in_archive(code)
        archived_link.wait_for(state="visible", timeout=10000)
        archived_link.hover()
        more_button = archived_link.get_by_test_id("iconButton")
        more_button.wait_for(state="visible", timeout=10000)
        more_button.click()
        self.page.get_by_text("Восстановить из архива", exact=True).click()
        self.page.get_by_role("button", name="Восстановить").click()
        expect(self.get_project_link(name)).to_be_visible(timeout=10000)

    # ------------------------------------------------------------------ #
    # ТК-3.6 Удаление проекта
    # ------------------------------------------------------------------ #
    def delete_project(self, name: str, code: str):
        self.open_project(name)
        self.open_board_menu(name)
        # Меню "три точки" тоже реализовано через role="dialog" (поповер),
        # поэтому после клика "Удалить" на странице одновременно два элемента
        # с role="dialog" — общий локатор [role='dialog'] становится
        # неоднозначным (strict mode violation). Явно берём именно диалог
        # подтверждения удаления по его тексту.
        confirm_dialog = self.page.get_by_role("dialog").filter(has_text="Удалить проект")
        self.page.get_by_text("Удалить", exact=True).click()
        confirm_dialog.wait_for(state="visible", timeout=10000)
        confirm_input = confirm_dialog.get_by_role("textbox")
        confirm_input.fill(code)
        confirm_dialog.get_by_role("button", name="Удалить", exact=True).click()
        confirm_dialog.wait_for(state="hidden", timeout=30000)
        self.navigate_to_projects_tab()
        expect(self.get_project_link(name)).not_to_be_visible(timeout=10000)

    # ------------------------------------------------------------------ #
    # ТК-3.7 / ТК-3.8 Избранное
    # ------------------------------------------------------------------ #
    def add_to_favorites(self, name: str):
        self.open_project(name)
        self.open_board_menu(name)
        menu_item = self.page.get_by_text("Добавить в избранное", exact=True)
        menu_item.click()
        # Дожидаемся закрытия пункта меню (значит, клик реально обработан),
        # прежде чем переходить на вкладку "Проекты" — иначе бывает гонка,
        # когда переход происходит раньше, чем на бэкенде/фронте
        # обновилось состояние "избранного" (наблюдалось на ТК-3.7).
        menu_item.wait_for(state="hidden", timeout=5000)
        self.navigate_to_projects_tab()
        self.favorites_heading.wait_for(state="visible", timeout=20000)
        expect(self._link_in_favorites(name)).to_be_visible(timeout=10000)

    def remove_from_favorites(self, name: str):
        self.open_project(name)
        self.open_board_menu(name)
        self.page.get_by_text("Убрать из избранного", exact=True).click()
        self.navigate_to_projects_tab()
        expect(self._link_in_favorites(name)).not_to_be_visible(timeout=10000)

    # ------------------------------------------------------------------ #
    # Общее
    # ------------------------------------------------------------------ #
    def check_error_message(self, expected_text: str):
        expect(self.page.get_by_text(expected_text)).to_be_visible()