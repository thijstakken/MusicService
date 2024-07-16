from flask import Blueprint

bp = Blueprint('settings', __name__)

from webapp.settings import routes