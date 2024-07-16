from flask import Blueprint

bp = Blueprint('errors', __name__)

from webapp.errors import handlers