from flask import Flask
from config import Config
from models import db
from flask import request
from models import Record
import json
from flask import make_response
from models import WebTarget, Source
from models import SocketTarget
from flask import render_template



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route("/record", methods=['POST'])
def record():
    ip = request.headers['X-Real-Ip'] if 'X-Real-Ip' in request.headers else "127.0.0.1"
    is_exist = Record.query.filter_by(
        url=request.json['url'],
        instance=ip).count()

    if not is_exist:
        record = Record(
            request.json['url'],
            ip,
            0, 0)
    else:
        record = Record.query.filter_by(
            url=request.json['url'],
            instance=ip).one()

    record.success += request.json['success']
    record.failure += request.json['failure']

    db.session.add(record)
    db.session.commit()

    return "Ok"
@app.route("/targets")
def targets():
    ip = request.headers['X-Real-Ip'] if 'X-Real-Ip' in request.headers else "127.0.0.1"
    is_exist = Source.query.filter_by(ip=ip).count()
    if is_exist:
        source = Source.query.filter_by(ip=ip).one()
    else:
        source = Source(ip, 0)

    source.treq += 1
    db.session.add(source)
    db.session.commit()

    targets = WebTarget.query.filter_by(is_active=True).order_by(WebTarget.id.desc()).all();
    targets = list(map(lambda t: t.url, targets))
    resp = make_response(json.dumps(targets))
    # resp.headers['Content-Type'] = "application/json; charset=UTF-8"
    return resp
@app.route("/targets/socket")
def socket_targets():
    targets = SocketTarget.query.filter_by(is_active=True).all();
    targets = list(map(lambda t: {
        'address': t.address,
        'port': t.port,
        'proto': t.proto }, targets))
    resp = make_response(json.dumps(targets))
    # resp.headers['Content-Type'] = "application/json; charset=UTF-8"
    return resp
@app.route('/')
def index1():
    ip = request.headers['X-Real-Ip'] if 'X-Real-Ip' in request.headers else "127.0.0.1"
    is_exist = Source.query.filter_by(ip=ip).count()
    if is_exist:
        source = Source.query.filter_by(ip=ip).one()
    else:
        source = Source(ip, 0)

    source.treq += 1
    db.session.add(source)
    db.session.commit()

    targets = WebTarget.query.filter_by(is_active=True).order_by(WebTarget.id.desc()).all()
    return render_template('jsgen1.html', targets=targets)
