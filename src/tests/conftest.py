import pytest
from playwright.sync_api import Playwright
import uuid
import os
import shutil

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


# Define paths to videos and screenshots directories
VIDEOS_DIR = '../videos'
SCREENSHOTS_DIR = '../screenshots'

def clear_directory(directory):
    """Delete all files and directories inside the specified directory."""
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

#ensures every session videos and screenshots are deleted
@pytest.fixture(scope='session', autouse=True)
def clear_videos_and_screenshots():
    """Fixture to clear videos and screenshots before tests run."""
    clear_directory(VIDEOS_DIR)
    clear_directory(SCREENSHOTS_DIR)
