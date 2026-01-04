import pytest
from playwright.sync_api import Playwright
import uuid
from pathlib import Path
import shutil
import os


@pytest.fixture(scope="function")
def setup_teardown(playwright: Playwright, request):
    browser = playwright.chromium.launch()
    repo_root = Path(__file__).parents[2]
    videos_dir = repo_root / "videos"
    logs_dir = repo_root / "logs"
    screenshots_dir = repo_root / "screenshots"
    # ensure dirs exist
    videos_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    # create per-test video directory so we can map videos to test node
    unique_id = uuid.uuid4().hex[:8]
    per_test_video_dir = videos_dir / unique_id
    per_test_video_dir.mkdir(parents=True, exist_ok=True)

    context = browser.new_context(record_video_dir=str(per_test_video_dir))
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto("https://www.saucedemo.com/")

    # attach video dir info to the test node for later reporting
    request.node._video_dir = per_test_video_dir

    yield page

    # teardown: capture screenshot, stop tracing, close context
    page.screenshot(path=str(screenshots_dir / f"snapshots_{unique_id}.png"))
    context.tracing.stop(path=str(logs_dir / f"tracing_{unique_id}.zip"))
    context.close()
    browser.close()

    # collect video files for the test node
    vids = []
    if per_test_video_dir.exists():
        for p in per_test_video_dir.rglob('*'):
            if p.is_file():
                vids.append(p)
    request.node._video_paths = vids
    # write metadata file linking this video folder to the test nodeid
    try:
        meta = {'nodeid': request.node.nodeid}
        import json

        (per_test_video_dir / 'metadata.json').write_text(json.dumps(meta))
    except Exception:
        pass


# Define paths to videos and screenshots directories relative to repo root
REPO_ROOT = Path(__file__).parents[2]
VIDEOS_DIR = REPO_ROOT / 'videos'
SCREENSHOTS_DIR = REPO_ROOT / 'screenshots'
LOGS_DIR = REPO_ROOT / 'logs'


def clear_directory(directory: Path):
    """Delete all files and directories inside the specified directory."""
    if directory.exists():
        for child in directory.iterdir():
            try:
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    shutil.rmtree(child)
            except Exception as e:
                print(f'Failed to delete {child}. Reason: {e}')


@pytest.fixture(scope='session', autouse=True)
def clear_videos_and_screenshots():
    """Fixture to clear videos, screenshots and logs before tests run."""
    for d in (VIDEOS_DIR, SCREENSHOTS_DIR, LOGS_DIR):
        clear_directory(d)


def _rel_path_from_reports(p: Path):
    try:
        return str(p.relative_to(REPO_ROOT))
    except Exception:
        return str(p)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach video links to pytest-html report when a test fails."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call' and rep.failed:
        video_paths = getattr(item, '_video_paths', None)
        if not video_paths:
            return
        try:
            from pytest_html import extras
        except Exception:
            extras = None
        if extras:
            extra = getattr(rep, 'extra', [])
            for vp in video_paths:
                rel = _rel_path_from_reports(vp)
                # link relative to the report location
                link = f"{rel}"
                extra.append(extras.html(f'<p>Video: <a href="{link}">{vp.name}</a></p>'))
            rep.extra = extra
