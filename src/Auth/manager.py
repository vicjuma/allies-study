from fastapi_login import LoginManager
from src.Auth.utils import SharedHandler

SECRET = "studyalliessiteforstudentsandtuitors"

manager = LoginManager(SECRET, "/auth/login",use_cookie=True)
manager.cookie_name = "studyalliescookie"

@manager.user_loader()
def load_user(username:str):
    sharedInst = SharedHandler()
    user = sharedInst.getBoth(username)
    return user
