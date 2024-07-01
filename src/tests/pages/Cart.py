from pages.Checkout import Checkout
class Cart:
    def __init__(self,page) -> None:
        self.page=page
        self.cart_title=page.locator("//span[@class='title']")
        self.cart_product_text=page.locator("//div[@class='inventory_item_name']")
        self.checkout_btn=page.locator("//button[@id='checkout']")
        
    def get_cart_page_title(self):
        return self.cart_title
    
    
    def get_cart_product_text(self):
        return self.cart_product_text
    
    def click_on_checkout(self):
        self.checkout_btn.click()
        return Checkout(self.page)
        