import pytest
from playwright.sync_api import expect
from pages.LoginPage import Loginpage


@pytest.mark.smoke
def test_add_to_cart(setup_teardown):
    page = setup_teardown
    login_page = Loginpage(page)
    credentials = {"username": "standard_user", "password": "secret_sauce"}
    inventory_page = login_page.do_login(credentials)
    expect(inventory_page.inventory_header).to_be_visible()
    expect(inventory_page.inventory_header).to_contain_text("Products")
    product_name = "Sauce Labs Backpack"
    inventory_page.click_addremove_to_cart(product_name)
    expect(inventory_page.get_addremove_to_cart_btn(
        product_name)).to_contain_text("Remove")


@pytest.mark.sanity
def test_remove_to_cart(setup_teardown):
    page = setup_teardown
    login_page = Loginpage(page)
    credentials = {"username": "standard_user", "password": "secret_sauce"}
    inventory_page = login_page.do_login(credentials)
    product_name = "Sauce Labs Backpack"
    inventory_page.click_addremove_to_cart(product_name)
    inventory_page.click_addremove_to_cart(product_name)
    expect(inventory_page.get_addremove_to_cart_btn(
        product_name)).to_contain_text("Add to cart")
