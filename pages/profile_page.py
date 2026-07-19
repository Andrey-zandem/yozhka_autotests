import re
from playwright.sync_api import Page, expect


class ProfilePage:
    def __init__(self, page: Page):
        self.page = page
        self.editable_fields = page.get_by_test_id("text-editable")
        self.inline_textbox = page.get_by_role("textbox", name="Заполнить")

        self.file_input = page.locator("input[type='file']")
        self.avatar_large = page.locator("[data-testid='avatar']._large_1jp4d_37")
        self.add_photo_button = page.get_by_text("Добавить фото")
        self.save_button = page.get_by_role("button", name="Сохранить", exact=True)
        
        self.open_profile_item = page.get_by_text("Открыть профиль", exact=True)

        self.account_actions_button = page.get_by_role("button", name="Действия с учётной записью")
        self.change_password_item = page.get_by_text("Изменить пароль", exact=True)
        self.old_password_input = page.get_by_role("textbox", name="Ведите старый пароль")
        self.new_password_input = page.get_by_role("textbox", name="Введите новый пароль")
        self.confirm_password_input = page.get_by_role("textbox", name="Такой же, как выше")
        self.change_password_button = page.get_by_role("button", name="Изменить пароль", exact=True)

        self.add_absence_button = page.get_by_test_id("popconfirm-button")
        self.absence_edit_button = page.get_by_test_id("popconfirm-button")

        self.delete_account_item = page.get_by_text("Удалить учётную запись")
        self.delete_confirm_input = page.get_by_role("textbox", name="Твоя почта")
        self.delete_confirm_button = page.get_by_role("button", name="Удалить", exact=True)
        self.final_delete_button = page.get_by_role("button", name="Удалить", exact=True)

    # ТК-4.1
    def open_profile(self, full_name: str):
        # Разбиваем имя на части и убираем первый элемент (инициалы)
        parts = full_name.split()
        if len(parts) >= 2:
            search_text = " ".join(parts[1:]) 
        else:
            search_text = full_name
        # Ищем ссылку по частичному совпадению
        user_link = self.page.get_by_role("link").filter(has_text=search_text)
        user_link.click()
        self.open_profile_item.wait_for(state="visible", timeout=15000)
        self.open_profile_item.click()
        self.page.wait_for_url(re.compile(r".*/user-profile/.*"), timeout=30000)
        self.page.get_by_text("Мой профиль", exact=False).wait_for(state="visible", timeout=15000)

    def change_avatar(self, file_path: str):
        # Ждём, пока input для загрузки станет доступен
        file_input = self.page.locator("input[type='file']")
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(file_path)
        # После загрузки файла нажимаем "Сохранить"
        self.save_button.click()

    # ТК-4.2/4.3/4.4/4.10
    def edit_field(self, field_index: int, value: str):
        field = self.editable_fields.nth(field_index)
        field.click()
        textbox = self.page.get_by_role("textbox", name="Заполнить")
        textbox.fill(value)
        textbox.press("Enter")

    # ТК-4.6/4.11/4.12
    def open_change_password_dialog(self):
        self.account_actions_button.click()
        self.change_password_item.click()

    def change_password(self, old_password: str, new_password: str):
        self.open_change_password_dialog()
        self.old_password_input.fill(old_password)
        self.new_password_input.fill(new_password)
        self.confirm_password_input.fill(new_password)
        self.change_password_button.click()

    # ТК-4.7/4.8
    def set_absence(self, start_day_name: str, end_day_name: str):
        self.add_absence_button.click()
        # Открываем календарь, кликая на поле "Выбери даты"
        self.page.get_by_role("textbox", name="Выбери даты").click()
        self.page.get_by_role("button", name=start_day_name).first.click()
        self.page.get_by_role("button", name=end_day_name).click()
        self.save_button.click()
        self.page.reload()

    def remove_absence(self):
        self.absence_edit_button.click()
        self.page.get_by_role("button", name="Удалить", exact=True).wait_for(state="visible", timeout=15000)
        self.page.get_by_role("button", name="Удалить", exact=True).click()

    # ТК-4.9/4.13/4.14
    def open_delete_account_dialog(self):
        self.account_actions_button.click()
        self.delete_account_item.click()
        # Ждём появления диалога 
        self.page.get_by_text("Удаление учётной записи", exact=False).wait_for(state="visible", timeout=10000)

    def delete_account(self, email: str, reason: str = ""):
        self.open_delete_account_dialog()
        self.final_delete_button.click()
        # Для аккаунта без пространств поле ввода почты должно появиться
        self.delete_confirm_input.wait_for(state="visible", timeout=10000)
        self.delete_confirm_input.fill(email)
        if reason:
            self.page.get_by_role("textbox", name="Напиши, почему решил(а) удалить учётную запись").fill(reason)
        self.delete_confirm_button.click()