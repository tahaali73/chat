from datetime import timedelta

class Config():
    SECRET_KEY = "29306ff4e76e20fdcfd2980ee0bf8748"
    JWT_SECRET_KEY = "e353c8cb1ec05cfaa94590dc1b3f477c"
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)  
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False  
    JWT_COOKIE_CSRF_PROTECT = True
    MONGO_URI = "mongodb+srv://diytech960:Qmobile888@cluster0.q0ffqok.mongodb.net/Chat_App"