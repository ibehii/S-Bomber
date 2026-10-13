<h1 align="center">SMS Bomber 💣</h1>
<h2 align="center"> <img src="https://skillicons.dev/icons?i=py,vscode,md,bots" alt="Technology skill icons: Python, VSCode, Markdown, Bots" />
<br>
<br>
<img src="https://img.shields.io/badge/Telegram-Account?logo=Telegram&label=Chat&labelColor=%23000000%20&color=%237a00eb%20&link=https://t.me/BZHNAM" alt="Telegram Chat Badge" /></h2>


_**⚠️ Important Notice: This program is intended for educational purposes only. We strongly advise against using it for any illegal activities. We are not responsible for any misuse of this program or its output.**_

### Contents :
- [Installation 📥](#installation-)
- [Usage 📖](#usage-)
- [CLI Options ⚙️](#cli-options-️)
- [Browser Depended SMS 🌐](#browser-depended-sms-)
- [Running Tests 🧪](#running-tests-)
---
# Installation 📥
1. Make sure you have **python** installed.
    * you can download it via [python official website](https://python.org).
2. Make sure you have git installed.
    * you can download it via [git official website](https://git-scm.com/).
3. Open a terminal
4. Run the following command to clone this repository:
    > git clone https://github.com/ibehii/S-Bomber
    * Also you can simply [**download**](https://github.com/ibehii/S-Bomber/archive/refs/heads/main.zip) the repository 
5. Change the directory to S-Bomber, By:
    > cd S-Bomber

6. download the dependency, by:
   > pip install -r requirements.txt

7. Run the Python file:
    > python Bomber.py

# Usage 📖
![S-Bomber CLI demonstration showing target phone number prompt and real-time execution logs](https://github.com/user-attachments/assets/a6d7a5d4-1747-4bf9-a874-9a233da5afb5)

At this stage enter a number and the program starts its execution.\
Iranian mobile numbers in domestic (`09123456789`), international (`+989123456789`), and Persian/Arabic numerals (`۰۹۱۲۳۴۵۶۷۸۹` / `٠٩١٢٣٤٥٦٧٨٩`) are fully supported.

# CLI Options ⚙️
You can run S-Bomber interactively or pass flags for automated workflows:
```bash
# Interactive mode (prompts for phone number):
python Bomber.py

# Non-interactive mode with options:
python Bomber.py --phone 09123456789
python Bomber.py --phone +989123456789 --interval 2.0 --no-browser
python Bomber.py --phone ۰۹۱۲۳۴۵۶۷۸۹ --only-browser
```

| Option | Shorthand | Description | Default |
|---|---|---|---|
| `--phone` | `-p` | Target Iranian mobile number (supports Persian/Arabic digits) | Interactive prompt |
| `--interval` | `-i` | Delay in seconds between requests | `1.6` |
| `--timeout` | `-t` | HTTP request timeout in seconds | `10.0` |
| `--no-browser` | | Skip browser automation phase (run only HTTP APIs) | `False` |
| `--only-browser` | | Run only browser automation phase | `False` |

# Browser Depended SMS 🌐
Some services had restrictions and couldn't mimic a valid behavior for them.\
The program will open a headless **FireFox** browser, but this action needs some requirements.
1. **FireFox** browser must be installed on your device.
    * You can download firefox from [their website](https://www.mozilla.org/en-US/firefox/download/thanks/)
2. Firefox **WebDriver** (`geckodriver`) should be located in the repository root (`S-Bomber/geckodriver`) or installed in system `PATH`.
   * S-Bomber can also automatically download and extract it when prompted.

# Running Tests 🧪
Run the automated test suite with standard Python `unittest`:
```bash
python -m unittest discover tests
```


---
Having trouble? Make an issue or send me a message on [telegram](https://t.me/BZHNAM)
