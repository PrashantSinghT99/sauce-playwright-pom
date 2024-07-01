import pytest
from playwright.sync_api import Playwright
import uuid

@pytest.fixture(scope="function")
def setup_teardown(playwright: Playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context(record_video_dir="videos")
    context.tracing.start(screenshots=True,snapshots=True,sources=True)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto("https://www.saucedemo.com/")
    yield page
    unique_id = str(uuid.uuid4())
    page.screenshot(path=f"screenshots/snapshots_{unique_id}.png")
    context.tracing.stop(path=f"logs/tracing_{unique_id}.zip")
    context.close()
    browser.close()
