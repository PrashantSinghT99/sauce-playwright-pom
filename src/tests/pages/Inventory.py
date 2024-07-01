from pages.Cart import Cart


class Inventory:
    def __init__(self, page) -> None:
        self.page = page
        self._inventory_header = page.locator("//span[@class='title']")
        self._hamburger_Btn = page.locator(
            "//button[@id='react-burger-menu-btn']")
        self._logout_btn = page.locator("//a[@id='logout_sidebar_link']")
        self.add_to_cart_btn = page.locator(
            "//div[text()='Sauce Labs Bike Light']/ancestor::div[@class='inventory_item_label']/following-sibling::div//button")
        self.cart_btn = page.locator("//a[@class='shopping_cart_link']")

    @property
    def inventory_header(self):
        return self._inventory_header

    def click_hamburger(self):
        return self._hamburger_Btn.click()

    def click_logout_btn(self):
        return self._logout_btn.click()

    def logout(self):
        self.click_hamburger()
        self.click_logout_btn()

    def get_addremove_to_cart_btn(self, text):
        return self.page.locator(f"//div[text()='{text}']/ancestor::div[@class='inventory_item_label']/following-sibling::div//button")

    def click_addremove_to_cart(self, product):
        self.get_addremove_to_cart_btn(product).click()
        return self

    def click_cart_btn(self):
        self.cart_btn.click()
        return Cart(self.page)
