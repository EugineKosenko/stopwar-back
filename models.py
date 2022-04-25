from flask_sqlalchemy import SQLAlchemy
import time

db = SQLAlchemy()
class Record(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    stamp = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    instance = db.Column(db.String(255), nullable=False)
    success = db.Column(db.Integer, nullable=False)
    failure = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('url', 'instance', name='unq_url_instance'),)

    def __init__(self, url, instance, success, failure):
        self.stamp = int(time.time())
        self.url = url
        self.instance = instance
        self.success = success
        self.failure = failure

    def __repr__(self):
        return str(self.url)
class Target(db.Model):
    __tablename__ = 'targets'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    ratio = db.Column(db.Float)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return str(self.url)
class Source(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), nullable=False, unique=True)
    treq = db.Column(db.Integer, nullable=False)

    def __init__(self, ip, treq):
        self.ip = ip
        self.treq = treq

    def __repr__(self):
        return str(self.ip)
class SocketTarget(db.Model):
    __tablename__ = 'socket_targets'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False)
    resource = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    proto = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (db.UniqueConstraint('address', 'port', 'proto', name='unq_target'),)

    def __init__(self, topic, resource, address, port, proto):
        self.topic = topic
        self.resource = resource
        self.address = address
        self.port = port
        self.proto = proto

    def __repr__(self):
        return str(self.address)

    def make(topic, resource, address, port, proto):
        targets = SocketTarget.query.filter_by(
            address=address,
            port=port,
            proto=proto)
    
        if targets.count() > 0:
            target = targets.one()
            target.topic = topic
            target.resource = resource
            target.is_active = True
        else:
            target = SocketTarget(topic, resource, address, port, proto)
    
        return target
class WebTarget(db.Model):
    __tablename__ = 'web_targets'

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False)
    resource = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, topic, resource, url):
        self.topic = topic
        self.resource = resource
        self.url = url

    def __repr__(self):
        return str(self.url)

    def make(topic, resource, url):
        targets = WebTarget.query.filter_by(url=url)
    
        if targets.count() > 0:
            target = targets.one()
            target.topic = topic
            target.resource = resource
            target.is_active = True
        else:
            target = WebTarget(topic, resource, url)
    
        return target
