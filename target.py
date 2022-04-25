from flask import Flask
from config import Config
from models import db



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route("/")
def record():
    print("Ok")
    return "Ok"
