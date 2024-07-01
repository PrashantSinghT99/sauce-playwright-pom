from playwright.sync_api import expect
from pages.LoginPage import Loginpage


def test_login_standard_user(setup_teardown):
    page = setup_teardown
    login_page = Loginpage(page)
    credentials = {"username": "standard_user", "password": "secret_sauce"}
    # page.pause()
    inventory_page = login_page.do_login(credentials)
    expect(inventory_page.inventory_header).to_be_visible()
    expect(inventory_page.inventory_header).to_contain_text("Products")


def test_login_locked_user(setup_teardown):
    page = setup_teardown
    login_page = Loginpage(page)
    credentials = {"username": "locked_out_user", "password": "secret_sauce"}
    login_page.do_login(credentials)
    expect(login_page.error_msg()).to_contain_text(
        "Epic sadface: Sorry, this user has been locked out.")


def test_login_no_user(setup_teardown):
    page = setup_teardown
    login_page = Loginpage(page)
    login_page.click_loginbtn()
    expect(login_page.error_msg()).to_contain_text(
        "Epic sadface: Username is required")


def test_unsafe_redirects(setup_teardown):
    page = setup_teardown
    page.goto("https://www.saucedemo.com/inventory.html")
    login_page = Loginpage(page)
    expect(login_page.error_msg()).to_contain_text(
        "Epic sadface: You can only access '/inventory.html' when you are logged in.")
