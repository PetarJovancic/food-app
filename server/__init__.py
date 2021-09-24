from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

server = Flask(__name__)
server.config.from_object(Config)
db = SQLAlchemy(server)
migrate = Migrate(server, db)

