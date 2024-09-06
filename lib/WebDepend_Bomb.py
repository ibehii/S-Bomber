# Github: https://github.com/ibehii
# Telegram: https://T.me/BZHNAM
# e-mail: Behii@tutanota.com
# ____________________________________________

# ======== # Import part # ======== # 
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.common.keys import Keys
    from pathlib import Path
except ImportError:
    exit('Some required module are missing.\nPlease run "path pip install -r requirements.txt" command on your terminal.')



class IranianWebSMS:
    '''Sending sms via browser. It's require webdriver and browser. [Fallow for more info]()
    "PhoneNumber": Target phone number.
    "driver": webdriver path on your system
    '''
    current_path: Path = Path(__file__).parent.resolve()
    def __init__(self, PhoneNumber: str, driver: Path = (current_path / "SeleniumFireFoxWebDriver" / 'geckodriver')) -> None:
        self.PhoneNumber: str = PhoneNumber
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(service=Service(executable_path= str(driver)), options=options)
        self.driver.implicitly_wait(7)

    def __exit__(self) -> None:
        self.driver.quit()
        
    def snapp_app_link(self) -> bool:
        URL: str = r"https://snapp.ir/"
        
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:
            inputBox = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lineHeight-d3-0-2-145')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

            
        
    def snapp_login_page(self) -> bool:
        URL: str = r'https://app.snapp.taxi/login/'
        
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:
            inputBox = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="مثلاً ۰۹۱۲۳۴۵۶۷۸۹"]')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

            
        
    def snapp_worker_login_page(self) -> bool:
        URL: str = r'https://digitalsignup.snapp.ir/'
        
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:
            inputBox = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'lineHeight-d3-0-2-39')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

               
    def snapp_food(self) -> bool:
        URL: str = r'https://snappfood.ir/'
        
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:
            inputBox = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'bhYsIv')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'kGePTa'))).click()
            inputBox = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[class="sc-hHftDr bhYsIv"]')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

               
    def snapp_market(self) -> bool:
        URL: str = r'https://snapp.market'
        
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'login-btn'))).click()
            inputBox = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'cellphone')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

               
    def snapp_trip(self) -> bool:
        URL: str = r"https://www.snapptrip.com/"
        
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="ورود و ثبت نام"]'))).click()
            inputBox = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="شماره موبایل"]')))
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.TAB, Keys.TAB, Keys.ENTER)

        except:
            return False
        else:
            return True

            
    
    def itoll(self) -> bool:
        URL: str = r"https://itoll.com/"
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'header-login-btn'))).click()
            inputBox = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'login-mobile')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

            

    def buskool(self) -> bool:
        URL: str = r"https://www.buskool.com/register"
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            inputBox = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'input-container'))).find_element(By.TAG_NAME, "input")
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True
        
        
    def nobat(self) -> bool:
        URL: str = r"https://user.nobat.ir/login"
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            inputBox = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'Login_mobileNumberInput__gJ58G')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

            
            
    def mihanpezeshk_patients(self) -> bool:
        URL: str = r"https://www.mihanpezeshk.com/loginPatient"
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            inputBox = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'form-group'))).find_element(By.TAG_NAME, 'input')
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

            
            
    def mihanpezeshk_doctor(self) -> bool:
        URL: str = r"https://www.mihanpezeshk.com/loginDoctor"
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            
            inputBox = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'form-group'))).find_element(By.TAG_NAME, 'input')
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
        except:
            return False
        else:
            return True

            
            
    def filimo(self) -> bool:
        URL: str = r"https://www.filimo.com/signin"
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            
            inputBox = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'username')))
            inputBox.clear()
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
            if(self.driver.title == 'فیلیمو - ورود'):
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'fFXRBO'))).click()
            else:
                self.driver.switch_to.new_window("tab")
                self.driver.get('https://www.filimo.com/signup/code')
                
        except:
            return False
        else:
            return True 
        
    def pooleno(self) -> bool:
        URL: str = r"https://pooleno.ir/"
        self.driver.get(URL)
        self.driver.maximize_window()
        
        try:    
            inputBox = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'form.flex:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > input:nth-child(1)')))
            inputBox.send_keys(self.PhoneNumber)
            inputBox.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, r'button.text-\[12px\]:nth-child(1)'))).click()
            
        except:
            return False
        else:
            return True 