import logging
from quart import (Blueprint, jsonify, render_template, abort, flash, request,
    redirect)
from quart_auth import AuthUser, login_user, logout_user, login_required
from jinja2 import TemplateNotFound
from potnanny.models.user import User, UserSchema, SessionUser
from potnanny.utils.password import verify_password, hash_password
from .forms import LoginForm, PasswordResetForm


logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__, template_folder='templates')


@bp.route('/login', methods=['GET', 'POST'])
async def login():
    form = await LoginForm.create_form()

    if await form.validate_on_submit():
        await request.get_data()
        username = (await request.form)["username"]
        password = (await request.form)["password"]

        try:
            u = await User.select().where(User.name == username).first()
            if u:
                if verify_password(password, u.password):
                    s = SessionUser(u.id)
                    s._user = u
                    s._resolved = True
                    login_user(s)
                    return redirect('/')
                else:
                    form.username.errors = ["login failure"]
            else:
                form.username.errors = ["login failure"]
        except Exception as x:
            logger.debug(str(x))
            form.username.errors = ["unexpected error"]

    try:
        return await render_template('auth/login.html', form=form)
    except TemplateNotFound:
        abort(404)


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
async def logout():
    logout_user()
    return redirect("/")


@bp.route('/pwreset', methods=['GET', 'POST'])
@login_required
async def pwreset():
    form = await PasswordResetForm.create_form()

    if await form.validate_on_submit():
        await request.get_data()
        username = (await request.form)["username"]
        existing = (await request.form)["current"]
        password = (await request.form)["password"]

        try:
            u = await User.select().where(User.name == username).first()
            if u:
                if verify_password(existing, u.password):
                    u.password = hash_password(password)
                    await u.save()
                    await flash('password successfully changed', 'success')
                    return redirect('/')
                else:
                    form.current.errors = ["login failure"]
            else:
                form.current.errors = ["user error"]
        except Exception as x:
            form.current.errors = ["unexpected error"]

    try:
        return await render_template('auth/reset.html', form=form)
    except TemplateNotFound:
        abort(404)
