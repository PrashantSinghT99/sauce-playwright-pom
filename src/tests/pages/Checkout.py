class Checkout:
    def __init__(self,page) -> None:
        self.page=page
        self.checkout_title=page.locator("//span[@class='title']")
        self.f_name=page.locator("//input[@id='first-name']")
        self.l_name=page.locator("//input[@id='last-name']")
        self.zip_code=page.locator("//input[@id='postal-code']")
        self.checkout_continue=page.locator("//input[@id='continue']")
        self.checkout_overview=page.locator("//span[@class='title']")
        self.checkout_finish_btn=page.locator("//button[@id='finish']")
        self.checkout_sucess_txt=page.locator("//h2[@class='complete-header']")
    
    def get_checkout_title(self):
        return self.checkout_title
    
    def enter_checkout_details(self,fname,lname,zip):
        self.f_name.fill(fname)
        self.l_name.fill(lname)
        self.zip_code.fill(zip)
        return self
        
    def click_checkout_continue(self):
        self.checkout_continue.click()
    
    def get_checkout_overview(self):
        return self.checkout_overview
    
    def click_checkout_finish_btn(self):
        self.checkout_finish_btn.click()
        
    def get_checkout_sucess(self):
        return self.checkout_sucess_txt
        
        
        
        
    
        