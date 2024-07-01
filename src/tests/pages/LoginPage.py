from pages.Inventory import Inventory


class Loginpage:

    def __init__(self, page):
        self.page = page
        self._username_locator = page.locator("//input[@id='user-name']")
        self._password_locator = page.locator("//input[@id='password']")
        self._login_btn_locator = page.locator("//input[@id='login-button']")
        self._error_msg = page.locator("//h3[@data-test='error']")
        self._loginPage_title = page.locator("//div[@class='login_logo']")

    def enter_username(self, user_name):
        self._username_locator.clear()
        self._username_locator.fill(user_name)

    def enter_password(self, password):
        self._password_locator.clear()
        self._password_locator.fill(password)

    def click_loginbtn(self):
        self._login_btn_locator.click()

    def do_login(self, credentials):
        self._username_locator.fill(credentials['username'])
        self._password_locator.fill(credentials['password'])
        self.click_loginbtn()
        return Inventory(self.page)

    def error_msg(self):
        return self._error_msg

    def loginPage_title(self):
        return self._loginPage_title
