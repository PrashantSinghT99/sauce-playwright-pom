import pytest
from playwright.sync_api import expect
from pages.LoginPage import Loginpage


@pytest.mark.sanity
def test_placeorder(setup_teardown):
    page = setup_teardown
    login_page = Loginpage(page)
    credentials = {"username": "standard_user", "password": "secret_sauce"}
    inventory_page = login_page.do_login(credentials)
    product_name = "Sauce Labs Onesie"
    # testing playwright chaining by returning self
    cart_page = inventory_page.click_addremove_to_cart(
        product_name).click_cart_btn()
    expect(cart_page.get_cart_page_title()).to_contain_text('Your Cart')
    expect(cart_page.get_cart_product_text()).to_contain_text(product_name)
    checkout_page = cart_page.click_on_checkout()
    expect(checkout_page.get_checkout_title()).to_contain_text(
        "Checkout: Your Information")
    # testing playwright chaining by returning self
    checkout_page.enter_checkout_details(
        "prashant", "singh", "12345678").click_checkout_continue()
    expect(checkout_page.get_checkout_overview()
           ).to_contain_text("Checkout: Overview")
    checkout_page.click_checkout_finish_btn()
    expect(checkout_page.get_checkout_sucess()).to_contain_text(
        "Thank you for your order!")
