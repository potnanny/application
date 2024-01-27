from quart import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


bp = Blueprint('about', __name__, template_folder='templates')


@bp.route('/about', methods=['GET'])
async def index():
    try:
        return await render_template('about/index.html')
    except TemplateNotFound:
        abort(404)
