from cryptography.fernet import Fernet
from src.settings import settings

def decrypt_mssg(mssg: str):
    key = settings.APP_FERMET_KEY    
    encoding = settings.ENCODING_STRING
    key = key.encode(encoding)
    fernet = Fernet(key)
    mssg = mssg.encode(encoding)
    return fernet.decrypt(mssg).decode(encoding)