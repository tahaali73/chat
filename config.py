from datetime import timedelta

class Config():
    SECRET_KEY = '8923yuhg3tgt348r7tnr3rji3hr'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)  
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = True  
    JWT_COOKIE_CSRF_PROTECT = True
    MONGO_URI = "mongodb+srv://diytech960:Qmobile888@cluster0.q0ffqok.mongodb.net/Chat_App"