from flask import Blueprint

bp = Blueprint('main', __name__)

from webapp.main import routes