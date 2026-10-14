<div align="center">

# 💣 S-Bomber
### *High-Performance SMS Provider Benchmarking & Stress-Testing Utility*

[![Release](https://img.shields.io/badge/Release-v1.2.0-purple?style=for-the-badge&logo=git&logoColor=white)](https://github.com/ibehii/S-Bomber/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Engine](https://img.shields.io/badge/Engine-Chrome%20%7C%20Firefox-FCC624?style=for-the-badge&logo=googlechrome&logoColor=black)](#-browser-acceleration--driver-matrix)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge&logo=open-source-initiative&logoColor=white)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-122%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](#-running-tests)
[![Telegram](https://img.shields.io/badge/Telegram-@dr__xz-0088cc?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/dr_xz)

<br/>

> **⚠️ Educational Notice & Disclaimer**
> 
> This tool is developed strictly for educational research, security testing, and provider resilience benchmarking. The author and contributors accept no responsibility or liability for unauthorized usage or unlawful activities.

</div>

---

### 🗺️ Quick Navigation

<table>
  <tr>
    <td align="center" width="20%">
      <a href="#-quick-start">
        <font size="6">🚀</font><br/>
        <b>Quick Start</b><br/>
        <sub>Launch in 30 seconds</sub>
      </a>
    </td>
    <td align="center" width="20%">
      <a href="#-key-features">
        <font size="6">✨</font><br/>
        <b>Key Features</b><br/>
        <sub>Core architecture & dials</sub>
      </a>
    </td>
    <td align="center" width="20%">
      <a href="#-browser-acceleration--driver-matrix">
        <font size="6">⚡</font><br/>
        <b>Browser Matrix</b><br/>
        <sub>Chrome & Firefox engines</sub>
      </a>
    </td>
    <td align="center" width="20%">
      <a href="#-proxy-pool--async-health-checker">
        <font size="6">🌐</font><br/>
        <b>Proxy Pool</b><br/>
        <sub>Async pings & live failover</sub>
      </a>
    </td>
    <td align="center" width="20%">
      <a href="#-configuration-file-configtoml">
        <font size="6">⚙️</font><br/>
        <b>Configuration</b><br/>
        <sub>Zero-typing config.toml</sub>
      </a>
    </td>
  </tr>
  <tr>
    <td align="center" width="20%">
      <a href="#-installation">
        <font size="6">📦</font><br/>
        <b>Installation</b><br/>
        <sub>Dependencies & setup</sub>
      </a>
    </td>
    <td align="center" width="20%">
      <a href="#-click-cli-reference">
        <font size="6">ℹ️</font><br/>
        <b>CLI Reference</b><br/>
        <sub>Options & subcommands</sub>
      </a>
    </td>
    <td align="center" width="20%">
      <a href="#-selective-service-dispatching">
        <font size="6">🎯</font><br/>
        <b>Service Filter</b><br/>
        <sub>Target specific endpoints</sub>
      </a>
    </td>
    <td align="center" width="20%">
      <a href="#-running-tests">
        <font size="6">🧪</font><br/>
        <b>Running Tests</b><br/>
        <sub>80 automated unit tests</sub>
      </a>
    </td>
    <td align="center" width="20%">
      <a href="#-troubleshooting">
        <font size="6">🔍</font><br/>
        <b>Troubleshooting</b><br/>
        <sub>Common fixes & solutions</sub>
      </a>
    </td>
  </tr>
</table>

---

<a id="-quick-start"></a>
## 🚀 Quick Start

Get started in seconds with either the interactive menu or direct flags:

```bash
# 1. Clone the repository
git clone https://github.com/ibehii/S-Bomber.git
cd S-Bomber

# 2. Install dependencies
pip install -r requirements.txt

# 3. Interactive Mode (renders interactive ASCII menu)
python Bomber.py

# 4. Direct CLI Execution (scriptable)
python Bomber.py -p 09123456789 -i 1.5 -d chrome

# 5. Check and clean proxy pool asynchronously
python Bomber.py check-proxies --prune
```

---

<a id="-key-features"></a>
## ✨ Key Features

| Feature | Description | Highlight |
| :--- | :--- | :--- |
| **Default Chrome Automation** | High-performance Google Chrome (`chromedriver`) integration via Selenium with automated Firefox fallback. | 🚀 Speed-first headless driver |
| **Speed-Optimized Browser Mode** | Accelerates runs via eager DOM parsing (`page_load_strategy="eager"`), disabled image rendering, and disabled GPU. | ⚡ Minimal latency & memory |
| **Click CLI & Dual Mode** | Rich Click CLI interface: launches an interactive ASCII menu when run without flags; executes directly when arguments are supplied. | 🕹️ Interactive & scriptable |
| **Async Proxy Pool & Pruner** | Concurrently tests proxies in `proxy.txt` via asynchronous TCP handshakes; tracks failures and offers auto-pruning. | 🌐 Concurrent health engine |
| **Live Dispatch Failover** | Automatically cycles to the next working proxy upon connection drop and logs dead nodes. | 🔄 Zero-interruption failover |
| **Persistent `config.toml`** | Stores default driver, headless preferences, timeouts, intervals, and proxy settings using Python 3.11+ `tomllib`. | ⚙️ Zero-typing configuration |
| **Selective Service Filtering** | Specify `--services digikala,divar,snapp_food` to target specific APIs across HTTP and browser engines. | 🎯 Targeted execution |
| **Full Number Normalization** | Intelligently normalizes Persian/Arabic numerals (`۰۱۲۳`), international (`+989...`), and domestic (`09...`) formats. | 📱 Robust input parsing |
| **Strict Security Sanitization** | All requests enforce sanitized headers, dynamic session IDs, and zero credential leakage. | 🛡️ Clean network footprint |

---

<a id="-browser-acceleration--driver-matrix"></a>
## ⚡ Browser Acceleration & Driver Matrix

S-Bomber features a dual-engine browser automation core designed to bypass API-only barriers:

| Engine | Default | Headless Flag | Page Load Strategy | Image Suppression | Fallback Support |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Google Chrome** | **Yes** (Primary) | `--headless=new` | `eager` (interactive DOM) | Native profile preferences (`images=2`) | Automatic fallback to Firefox |
| **Mozilla Firefox** | Fallback / Explicit | `--headless` | `eager` (interactive DOM) | Preference `permissions.default.image=2` | Bundled & system `geckodriver` resolver |

### Speed Optimizations Under the Hood:
- **`page_load_strategy = "eager"`**: Halts blocking wait once `DOMContentLoaded` fires, eliminating delays from third-party analytics, fonts, and trackers.
- **Image Suppression**: Disables downloading JPG/PNG/WebP assets to dramatically conserve network bandwidth.
- **GPU Overhead Disabled**: Enforces `--disable-gpu`, `--no-sandbox`, and `--disable-dev-shm-usage` for minimal container footprints.

---

<a id="-proxy-pool--async-health-checker"></a>
## 🌐 Proxy Pool & Async Health Checker

Manage and rotate proxies effortlessly via `proxy.txt`:

### Supported Proxy URI Schemes
```text
# IP:Port (defaults to HTTP)
192.168.1.100:8080

# Explicit HTTP / HTTPS
http://username:password@proxy.example.com:3128
https://10.0.0.1:8443

# SOCKS5
socks5://127.0.0.1:1080
```

### Standalone Health Check Subcommand
```bash
# Verify all proxies in proxy.txt with 3.5s timeout
python Bomber.py check-proxies

# Auto-prune dead proxies without interactive prompt
python Bomber.py check-proxies --prune --timeout 2.0
```

During execution, alive proxies display in **GREEN** with round-trip latency, while dead proxies display in **RED**. At run completion, S-Bomber offers to prune dead proxies from your file.

---

<a id="-configuration-file-configtoml"></a>
## ⚙️ Configuration File (`config.toml`)

Persistent configuration is managed via `config.toml` in the repository root. Any CLI flag will cleanly override these values at runtime:

```toml
# S-Bomber Configuration File

[general]
telegram = "https://t.me/dr_xz"
github = "https://github.com/ibehii"
version = "1.2.0"

[bomber]
# Primary browser engine: "chrome" (recommended) or "firefox"
default_driver = "chrome"

# Whether to execute browser automation services after HTTP services
use_browser = true

# Request interval delay in seconds between consecutive dispatches
request_interval = 1.6

# HTTP connection and read timeout in seconds
request_timeout = 10.0

# Run browser in headless mode (no GUI window displayed)
is_headless = true

# Optimize browser performance by disabling image rendering and using eager DOM loading
fast_browser_mode = true

# Path to proxy file containing one proxy per line
proxy_file = "proxy.txt"

# Limit execution to specific services, e.g. ["divar", "digikala"]. Empty runs all services.
selected_services = []
```

---

<a id="-installation"></a>
## 📦 Installation

### Prerequisites
- **Python 3.10+** (Python 3.11+ recommended for built-in `tomllib`)
- **Google Chrome** & `chromedriver` (or **Firefox** & `geckodriver`)

### Step-by-Step Setup
```bash
# 1. Clone repository
git clone https://github.com/ibehii/S-Bomber.git
cd S-Bomber

# 2. (Optional) Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

<a id="-click-cli-reference"></a>
## ℹ️ Click CLI Reference

### Main Command Options

| Option | Flag | Type | Description | Default |
| :--- | :---: | :---: | :--- | :--- |
| `--phone` | `-p` | `TEXT` | Target Iranian mobile number (supports Persian/Arabic digits) | Interactive prompt |
| `--interval` | `-i` | `FLOAT` | Interval in seconds between consecutive requests | `1.6` (or config) |
| `--timeout` | `-t` | `FLOAT` | Outgoing HTTP request timeout in seconds | `10.0` (or config) |
| `--driver` | `-d` | `[chrome\|firefox]` | Browser automation engine | `chrome` |
| `--services` | `-s` | `TEXT` | Comma-separated list of services (e.g. `divar,snapp_food`) | All services |
| `--tags` | `-g` | `TEXT` | Category tags to target (e.g. `transport,marketplace,food`) | All categories |
| `--proxy-file` | | `PATH` | Custom path to proxy list file | `proxy.txt` |
| `--only-browser` | | `FLAG` | Run only browser automation services | `False` |
| `--no-browser` | | `FLAG` | Run only HTTP API services | `False` |
| `--headless / --no-headless` | | `BOOLEAN` | Toggle browser headless display | `True` |
| `--rich / --no-rich` | | `BOOLEAN` | Toggle live Rich terminal dashboard | `True` |
| `--export / --no-export` | | `BOOLEAN` | Export benchmark telemetry report after run | `False` |
| `--export-format` | | `[json\|csv\|md]` | Report export format | `json` |
| `--reports-dir` | | `PATH` | Directory where benchmark reports are saved | `reports` |
| `--rounds` | `-r` | `INTEGER` | Number of execution rounds to dispatch | `1` |
| `--round-interval` | | `FLOAT` | Delay in seconds between consecutive rounds | `5.0` |
| `--config` | `-c` | `PATH` | Custom path to `config.toml` | `config.toml` |
| `--help` | | `FLAG` | Show CLI help message and exit | |

### Subcommands

```bash
# 1. Asynchronously test and clean proxies
python Bomber.py check-proxies [--proxy-file PATH] [--timeout SECONDS] [--prune]

# 2. Non-intrusively verify availability of service provider endpoints
python Bomber.py check-services [--timeout SECONDS] [--tag CATEGORY]

# 3. Scrape public proxy repositories and auto-populate proxy.txt with live nodes
python Bomber.py update-proxies [--proxy-file PATH] [--max-proxies INTEGER] [--timeout SECONDS]
```

---

<a id="-selective-service-dispatching"></a>
## 🎯 Selective Service Dispatching

Route requests specifically to selected services without running the entire suite:

```bash
# Run only Divar and Snapp Food
python Bomber.py -p 09123456789 --services divar,snapp_food

# Target browser-only services
python Bomber.py -p 09123456789 --only-browser --services snapp_app_link,buskool
```

---

<a id="-running-tests"></a>
## 🧪 Running Tests

S-Bomber includes a comprehensive automated test suite with 122 unit and regression tests:

```bash
# Discover and run all test modules
python3 -m unittest discover tests -v
```

### Test Coverage Highlights:
- **`test_config_loader.py`**: TOML configuration parsing, fallback defaults, and multi-round/report settings.
- **`test_proxy_manager.py`**: Proxy normalization, asynchronous TCP handshake verification, round-robin pooling, and dead proxy pruning.
- **`test_proxy_updater.py`**: Public proxy list scraping, candidate deduplication, and automated live node file updates.
- **`test_click_cli.py`**: Click CLI arguments, `--services`, `--tags`, `--rounds`, `--export`, and all subcommands via `CliRunner`.
- **`test_dashboard.py`**: Rich console tables, progress bar updates, stats calculation, and graceful ASCII fallbacks.
- **`test_reporter.py`**: JSON, CSV, and Markdown telemetry export with phone number masking.
- **`test_service_tags.py`**: Category grouping, tag validation, and multi-tag filtering.
- **`test_service_checker.py`**: Non-intrusive HEAD/GET reachability checks and endpoint error handling.
- **`test_driver_manager.py`**: Automated WebDriver resolution via `webdriver-manager` and system PATH fallback.
- **`test_web_sms.py`**: Chrome WebDriver initialization, eager DOM strategies, and Firefox fallback mechanism.
- **`test_security_and_headers.py`**: Header sanitization, dynamic session IDs, and credential omission checks.
- **`test_phone_normalization.py`**: Persian, Arabic, domestic, and international phone number normalization.

---

<a id="-troubleshooting"></a>
## 🔍 Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `ChromeDriver binary missing` | Chrome or chromedriver is not in `PATH` | S-Bomber automatically falls back to Firefox. Or install chromedriver via package manager (`apt install chromium-chromedriver` / `brew install chromedriver`). |
| `All proxies marked dead` | Restrictive firewall or offline proxies | Verify network access or run `python Bomber.py check-proxies -t 5.0` with a higher timeout. |
| `ImportError: tomllib` | Python version is earlier than 3.11 | Run `pip install tomli` or upgrade to Python 3.11+. S-Bomber includes automatic `tomli` fallback. |
| `Validation error: Invalid phone` | Non-Iranian number or invalid length | Provide a standard 10-13 character Iranian mobile number starting with `09`, `989`, or `+989`. |

---

<div align="center">

### 📬 Author & Community

Have questions or feedback? Connect via Telegram:

[![Telegram Channel](https://img.shields.io/badge/Telegram-@dr__xz-0088cc?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/dr_xz)
[![GitHub](https://img.shields.io/badge/GitHub-ibehii-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ibehii)

</div>
