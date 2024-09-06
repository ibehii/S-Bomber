#  GitHub: https://github.com/beh185
#  Telegram: https://T.me/BZHNAM
#  e-mail: Behii@tutanota.com
#  ____________________________________________

class BombServerError(Exception):
    '''Occur when Server doesn't respond'''
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
    def __str__(self) -> str:
        return "The server doesn't respond"

class BombClientError(Exception):
    '''Occur when The server cannot or will not process the request due to something that is perceived to be a client error'''
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
    def __str__(self) -> str:
        return "The server doesn't respond" 