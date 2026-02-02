# Defines the Blueprint
from flask import Blueprint

z83_bp = Blueprint('z83', __name__, template_folder='templates', static_folder='static')

from . import routes  # noqa: E402, F401
