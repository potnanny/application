import logging
import base64
import json
from quart import (Blueprint, jsonify, render_template, abort, flash, request,
    redirect)
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.database import db
from potnanny.models.keychain import Keychain, KeychainSchema
from potnanny.models.license import License
from .forms import LicenseForm
from .controllers import load_license


logger = logging.getLogger(__name__)
bp = Blueprint('features', __name__, template_folder='templates')


@bp.route('/features', methods=['GET'])
@login_required
async def show_features():
    results = await License.select()

    try:
        return await render_template('features/index.html', data=results)
    except TemplateNotFound:
        abort(404)


@bp.route('/features/import', methods=['GET', 'POST'])
@login_required
async def import_key():
    form = await LicenseForm.create_form()

    if await form.validate_on_submit():
        await request.get_data()
        raw = (await request.form)["license"]
        data = {}

        try:
            b = base64.b64decode(raw)
            logger.debug(b)

            data = json.loads(b)
            logger.debug(data)
            rval, msg = await load_license(data)
            if rval:
                if not getattr(form.license, 'errors'):
                    form.license.errors = []
                form.license.errors.append(msg)

        except Exception as x:
            logger.warning(x)
            if not getattr(form.license, 'errors'):
                form.license.errors = []
            form.license.errors.append('error decoding key')

        if not getattr(form.license, 'errors'):
            await flash('feature license loaded', 'info')
            return redirect("/")
    try:
        return await render_template('features/form.html', form=form)
    except TemplateNotFound:
        abort(404)
