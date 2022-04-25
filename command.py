from flask import Flask
from config import Config
from flask.cli import AppGroup
import click
from models import db, Target
import yaml
from models import SocketTarget, WebTarget
import re

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
target = AppGroup('target')
app.cli.add_command(target)
@target.command('add')
@click.argument('url')
def add_target(url):
    is_exist = Target.query.filter_by(url=url).count()

    if not is_exist:
        target = Target(url)
    else:
        target = Target.query.filter_by(url=url).one()
        target.is_active = True

    db.session.add(target)
    db.session.commit()
@target.command('remove')
@click.argument('url')
def remove_target(url):
    is_exist = Target.query.filter_by(url=url).count()

    if is_exist:
        target = Target.query.filter_by(url=url).one()
        target.is_active = False

    db.session.add(target)
    db.session.commit()
@target.command('ratio')
def ratio():
    targets = Target.query.all()

    for t in targets:
        with db.engine.connect() as c:
            rows = c.execute(f"select url, sum(failure)/(sum(success)+sum(failure)) rate from records group by url having url='%s'" % t.url)
            for r in rows:
                t.ratio = r[1]

            db.session.add(t)

    db.session.commit()
@target.command('file')
@click.argument('name')
def add_targets(name):
    with open(name, 'r') as f:
        data = yaml.safe_load(f)
        for topic in data['topics']:
            for resource in topic['resources']:
                for target in resource['targets']:
                    web, socket = parse_target(target)
                    for dest in socket:
                        db.session.add(SocketTarget.make(
                            topic['name'], resource['name'],
                            dest['address'], dest['port'], dest['proto']))
                    for dest in web:
                        db.session.add(WebTarget.make(
                            topic['name'], resource['name'],
                            dest))
        db.session.commit()
def parse_target(source):
    web = []
    socket = []
    result = (web, socket)
    if re.search(r"^http", source):
        m = re.fullmatch(r"(http|https)://([a-z0-9\-\.]+)(.*)", source)
        if m[1] == 'http':
            port = 80
        elif m[1] == 'https':
            port = 443
        else:
            raise "Неправильный протокол"
        if m[3] == "":
              source += "/"
        web.append(source)
        socket.append({
            'address': m[2],
            'port': port,
            'proto': 'tcp'})
    else:
        m = re.fullmatch(r"([^ ]+) \(([^\)]+)\)", source)
        address, ports = m[1], m[2].split(", ")
        for p in ports:
            port, proto = p.split("/")
            port = int(port)
            if proto in ['http', 'https']:
                proto = 'tcp'
            socket.append({
                'address': address,
                'port': port,
                'proto': proto})
            if port == 80 and proto == 'tcp' :
                web.append(f"http://%s/" % address)
            elif port == 443 and proto == 'tcp':
                web.append(f"https://%s/" % address)
        pass
    return result
