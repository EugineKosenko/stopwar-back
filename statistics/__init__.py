from flask import Flask
from config import Config
from models import db
from flask import render_template
from flask import request



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route("/")
def index():
    return render_template("test.html")
@app.route("/test", methods=['POST'])
def test():
    print(request.headers)
    print(request.json)
    return 'Ok'
