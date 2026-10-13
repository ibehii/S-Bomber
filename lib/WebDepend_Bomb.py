# Github: https://github.com/ibehii
# Telegram: https://T.me/BZHNAM
# e-mail: Behii@tutanota.com
# ____________________________________________

"""Browser-automated SMS dispatching using Selenium and headless Firefox."""

from pathlib import Path
import shutil
from types import TracebackType
from typing import Any

try:
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.support import expected_conditions as ExpectedConditions
    from selenium.webdriver.support.wait import WebDriverWait

    SELENIUM_AVAILABLE: bool = True
except ImportError:
    SELENIUM_AVAILABLE = False
    webdriver = None  # type: ignore[assignment]
    WebDriverException = Exception  # type: ignore[assignment, misc]
    TimeoutException = Exception  # type: ignore[assignment, misc]
    FirefoxOptions = None  # type: ignore[assignment, misc]
    FirefoxService = None  # type: ignore[assignment, misc]


class IranianWebSMS:
    """Dispatches SMS verification requests via headless Firefox browser automation.

    Parameters
    ----------
    phone_number : str
        Target Iranian phone number.
    driver_executable_path : Path | str | None, optional
        Path to the geckodriver binary. If None, checks repository root then system PATH.
    is_headless : bool, optional
        Whether to run Firefox in headless mode, by default True.
    """

    def __init__(
        self,
        phone_number: str,
        driver_executable_path: Path | str | None = None,
        is_headless: bool = True,
    ) -> None:
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium is required to use IranianWebSMS. "
                "Please install it with: pip install selenium"
            )

        self.phone_number: str = phone_number
        # Maintain backward-compatible attribute
        self.PhoneNumber: str = phone_number

        resolved_driver_path: Path | str | None = driver_executable_path
        if resolved_driver_path is None:
            local_geckodriver: Path = (
                Path(__file__).parent.parent.resolve() / "geckodriver"
            )
            if local_geckodriver.exists() and local_geckodriver.is_file():
                resolved_driver_path = local_geckodriver
            else:
                system_geckodriver = shutil.which("geckodriver")
                if system_geckodriver is not None:
                    resolved_driver_path = system_geckodriver

        firefox_options = FirefoxOptions()
        if is_headless:
            firefox_options.add_argument("--headless")

        service_kwargs: dict[str, Any] = {}
        if resolved_driver_path is not None and (
            (isinstance(resolved_driver_path, Path) and resolved_driver_path.exists())
            or (isinstance(resolved_driver_path, str) and Path(resolved_driver_path).exists())
        ):
            service_kwargs["executable_path"] = str(resolved_driver_path)

        firefox_service = FirefoxService(**service_kwargs)
        self.driver: Any = webdriver.Firefox(
            service=firefox_service,
            options=firefox_options,
        )
        self.driver.implicitly_wait(7)

    def __enter__(self) -> "IranianWebSMS":
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        """Safely terminate the browser process and release system resources."""
        active_driver = getattr(self, "driver", None)
        if active_driver is not None:
            try:
                active_driver.quit()
            except Exception:
                pass
            finally:
                self.driver = None

    @classmethod
    def get_service_methods(cls) -> list[str]:
        """Return an ordered list of callable browser SMS provider service method names."""
        excluded_attribute_names: set[str] = {
            "close",
            "get_service_methods",
        }
        return [
            method_name
            for method_name in dir(cls)
            if not method_name.startswith("_")
            and method_name not in excluded_attribute_names
            and callable(getattr(cls, method_name))
        ]

    # ==================== Web Service Provider Methods ==================== #

    def snapp_app_link(self) -> bool:
        """Send Snapp application download link via SMS."""
        target_url: str = "https://snapp.ir/"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.visibility_of_element_located(
                    (By.CLASS_NAME, "lineHeight-d3-0-2-145")
                )
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def snapp_login_page(self) -> bool:
        """Send Snapp passenger login verification code via SMS."""
        target_url: str = "https://app.snapp.taxi/login/"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[placeholder="مثلاً ۰۹۱۲۳۴۵۶۷۸۹"]')
                )
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def snapp_worker_login_page(self) -> bool:
        """Send Snapp digital signup driver registration SMS."""
        target_url: str = "https://digitalsignup.snapp.ir/"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.CLASS_NAME, "lineHeight-d3-0-2-39")
                )
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def snapp_food(self) -> bool:
        """Send Snappfood login verification code via SMS."""
        target_url: str = "https://snappfood.ir/"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.CLASS_NAME, "bhYsIv")
                )
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)

            login_trigger_button = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.CLASS_NAME, "kGePTa")
                )
            )
            login_trigger_button.click()

            secondary_phone_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[class="sc-hHftDr bhYsIv"]')
                )
            )
            secondary_phone_field.clear()
            secondary_phone_field.send_keys(self.phone_number)
            secondary_phone_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def snapp_market(self) -> bool:
        """Send Snapp Market login verification code via SMS."""
        target_url: str = "https://snapp.market"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            login_button = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.CLASS_NAME, "login-btn")
                )
            )
            login_button.click()
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.ID, "cellphone")
                )
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def snapp_trip(self) -> bool:
        """Send Snapptrip login verification code via SMS."""
        target_url: str = "https://www.snapptrip.com/"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            login_button = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[aria-label="ورود و ثبت نام"]')
                )
            )
            login_button.click()
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'input[placeholder="شماره موبایل"]')
                )
            )
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.TAB, Keys.TAB, Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def itoll(self) -> bool:
        """Send Itoll login verification code via SMS."""
        target_url: str = "https://itoll.com/"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            login_button = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.presence_of_element_located(
                    (By.ID, "header-login-btn")
                )
            )
            login_button.click()
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.visibility_of_element_located(
                    (By.ID, "login-mobile")
                )
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def buskool(self) -> bool:
        """Send Buskool registration verification code via SMS."""
        target_url: str = "https://www.buskool.com/register"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            phone_input_container = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.visibility_of_element_located(
                    (By.CLASS_NAME, "input-container")
                )
            )
            phone_input_field = phone_input_container.find_element(
                By.TAG_NAME, "input"
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def nobat(self) -> bool:
        """Send Nobat.ir login verification code via SMS."""
        target_url: str = "https://user.nobat.ir/login"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.visibility_of_element_located(
                    (By.CLASS_NAME, "Login_mobileNumberInput__gJ58G")
                )
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def mihanpezeshk_patients(self) -> bool:
        """Send Mihanpezeshk patient login verification code via SMS."""
        target_url: str = "https://www.mihanpezeshk.com/loginPatient"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            form_group_element = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.visibility_of_element_located(
                    (By.CLASS_NAME, "form-group")
                )
            )
            phone_input_field = form_group_element.find_element(
                By.TAG_NAME, "input"
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def mihanpezeshk_doctor(self) -> bool:
        """Send Mihanpezeshk doctor login verification code via SMS."""
        target_url: str = "https://www.mihanpezeshk.com/loginDoctor"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            form_group_element = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.visibility_of_element_located(
                    (By.CLASS_NAME, "form-group")
                )
            )
            phone_input_field = form_group_element.find_element(
                By.TAG_NAME, "input"
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True

    def filimo(self) -> bool:
        """Send Filimo signin verification code via SMS."""
        target_url: str = "https://www.filimo.com/signin"
        original_window_handle: str = ""
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            original_window_handle = self.driver.current_window_handle
            phone_input_field = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.visibility_of_element_located(
                    (By.ID, "username")
                )
            )
            phone_input_field.clear()
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)

            if self.driver.title == "فیلیمو - ورود":
                otp_request_element = WebDriverWait(self.driver, 10).until(
                    ExpectedConditions.visibility_of_element_located(
                        (By.CLASS_NAME, "fFXRBO")
                    )
                )
                otp_request_element.click()
            else:
                self.driver.switch_to.new_window("tab")
                self.driver.get("https://www.filimo.com/signup/code")
                # Clean up newly opened tab to avoid tab proliferation
                if original_window_handle and len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window_handle)
        except (WebDriverException, TimeoutException, Exception):
            try:
                if (
                    self.driver is not None
                    and original_window_handle
                    and original_window_handle in self.driver.window_handles
                ):
                    self.driver.switch_to.window(original_window_handle)
            except Exception:
                pass
            return False
        return True

    def pooleno(self) -> bool:
        """Send Pooleno registration verification code via SMS."""
        target_url: str = "https://pooleno.ir/"
        try:
            self.driver.get(target_url)
            self.driver.maximize_window()
            phone_input_field = WebDriverWait(self.driver, 15).until(
                ExpectedConditions.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "form.flex:nth-child(3) > div:nth-child(1) > div:nth-child(1) "
                        "> div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > input:nth-child(1)",
                    )
                )
            )
            phone_input_field.send_keys(self.phone_number)
            phone_input_field.send_keys(Keys.ENTER)
            submit_action_button = WebDriverWait(self.driver, 10).until(
                ExpectedConditions.element_to_be_clickable(
                    (By.CSS_SELECTOR, r"button.text-\[12px\]:nth-child(1)")
                )
            )
            submit_action_button.click()
        except (WebDriverException, TimeoutException, Exception):
            return False
        return True


__all__ = ["IranianWebSMS", "SELENIUM_AVAILABLE"]