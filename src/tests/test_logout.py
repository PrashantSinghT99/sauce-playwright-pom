import pytest
from playwright.sync_api import expect
from pages.LoginPage import Loginpage


@pytest.mark.smoke
def test_logout_standard_user(setup_teardown) -> None:
    page = setup_teardown
    login_page = Loginpage(page)
    credentials = {"username": "standard_user", "password": "secret_sauce"}
    inventory_page = login_page.do_login(credentials)
    expect(inventory_page.inventory_header).to_be_visible()
    expect(inventory_page.inventory_header).to_contain_text("Products")
    inventory_page.logout()
    expect(login_page.loginPage_title()).to_contain_text('Swag Labs')
