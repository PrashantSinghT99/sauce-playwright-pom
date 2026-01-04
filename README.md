# Sauce Playwright POM Framework

A lightweight yet robust test automation framework designed for **learning and architectural demonstration**.  
It utilizes the **Page Object Model (POM)** pattern, a custom **Click-based CLI orchestrator**, and **Pytest** to handle UI automation with Playwright.

This project goes beyond basic test scripts to demonstrate advanced SDET capabilities such as session persistence, dynamic test discovery, parallel execution orchestration, and an optional HTTP API runner.

---

## 🚀 Key Features

- **Custom CLI Runner**
  - Centralized entry point (`runner.py`) using `click`
  - Easy-to-use flags for controlled execution

- **Smart Execution**
  - **Parallel Execution:** Concurrent test runs using `pytest-xdist`
  - **Folder & File Discovery:** Deep scanning for targeted execution
  - **Retry Mechanism:** Automatic retries for flaky tests via `pytest-rerunfailures`

- **Session Management**
  - **Session Persistence:** Resume previous runs and re-run only failed tests
  - **Auto-Cleanup:** Clears logs, screenshots, and reports before new runs

- **Rich Reporting**
  - Consolidated HTML reports
  - Automatic screenshot capture on failures
  - Optional video recording via flags
  - Execution duration tracking with Pie Chart visualization

- **High Performance**
  - Optimized dependency management and execution using **uv**

---

## 🛠️ Project Structure

```text
sauce-playwright-pom/
├── src/
│   ├── pages/           # Page Object Model classes
│   └── tests/           # Test scripts (test_*.py)
├── reports/             # HTML reports, Screenshots, Videos
├── logs/                # Execution logs
├── runner.py            # Custom CLI Orchestrator
├── conftest.py          # Pytest hooks (Screenshots, Browser setup)
├── Makefile             # Short commands for easy management
├── pyproject.toml       # Dependencies & Tool configuration
└── requirements.txt     # Legacy dependency file
```

---

## ⚙️ Quick Setup

### 1. Create and activate a virtual environment

```bash
# Using standard Python
python3 -m venv .venv
source .venv/bin/activate

# OR using uv (Recommended)
uv venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
# Using pip
pip install -r requirements.txt

# OR using uv
uv sync
```

### 3. Install Playwright browsers

```bash
playwright install
```

---

## 🏃 Usage

### Option 1: Custom Runner (Recommended)

The `runner.py` script provides granular control over test execution.

**Basic run**
```bash
python runner.py
```

**Parallel execution (3 workers)**
```bash
python runner.py --parallel 3
```

**Run a specific file or folder**
```bash
python runner.py --target src/tests/login/
```

**Run with retries and video recording**
```bash
python runner.py --retries 2 --video
```

#### Full Command Options

| Flag | Short | Description |
|------|-------|-------------|
| `--target` | `-t` | Path to file or folder to run (Default: `src/tests`) |
| `--parallel` | `-p` | Number of parallel workers (Default: 1) |
| `--tags` | `-m` | Filter by pytest markers (e.g., smoke, sanity) |
| `--retries` | `-r` | Number of retries for failed tests |
| `--clean` | — | Clear reports and logs before execution |
| `--video` | — | Enable video recording |
| `--browser` | — | Browser choice: chromium, firefox, webkit |

### Option 2: Makefile Targets

Shortcuts for common workflows.  
The Makefile prefers `uv run` if available.

```bash
make install   # Create venv and install dependencies
make run       # Discover & run all tests
make smoke     # Run smoke tests
make sanity    # Run sanity tests
make clear     # Remove reports, videos, screenshots, logs
make resume    # Resume last session (re-run failed tests)
make api       # Start FastAPI runner using uvicorn
```

---

## 📊 Reporting

After execution, all artifacts are stored in the `reports/` directory:

- **HTML Report:** `report.html` with results, execution time, and environment info
- **Screenshots:** Automatically captured and attached on failures
- **Logs:** Detailed execution logs in `logs/session.log`

---

## 💡 Using uv run

This project supports `uv`, a fast Python package manager.

- Faster Python startup and dependency resolution
- Makefile auto-detects `uv`
- Falls back to virtualenv Python if `uv` is unavailable