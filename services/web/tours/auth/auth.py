from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, session
from flask.views import View
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from wtforms.validators import ValidationError
from ..models import Users
from .forms import LogInForm, SignUpForm
from .. import db
from ..utils import make_header


auth_bp = Blueprint('auth_bp', __name__,
                    url_prefix='/auth',
                    static_folder='static',
                    template_folder='templates'
                    )


class Login(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        form = LogInForm()

        if form.validate_on_submit():
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            user = db.session.execute(db.select(Users).where(Users.username == username)).scalar()

            if not user or not check_password_hash(user.password, password):
                flash(_('E-mail o password errate! Riprova...'), category='error')
                return redirect(url_for('auth_bp.login'))
            login_user(user, remember=remember)
            current_app.session_interface.regenerate(session)
            current_app.logger.info(f"Login utente {username}")
            return redirect(url_for('start'))

        lang = session['lang']
        header = make_header(lang)
        return render_template("login.jinja2", form=form, header=header)


class SignUp(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        form = SignUpForm()

        if form.validate_on_submit():
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            error = None

            if not username:
                error = _('il campo "username" è obbligatorio')
            elif not password:
                error = _('Il campo "password" è obbligatorio')
            elif not email:
                error = _('Il campo "e-mail" è obbligatorio')

            if not error:
                new_user = Users(
                    username=username,
                    password=generate_password_hash(password),
                    email=email
                )
                db.session.add(new_user)
                try:
                    db.session.commit()
                except IntegrityError:
                    error = _(f"Un utente con username {username} è già registrato")
                else:
                    return redirect(url_for('auth_bp.login'))

            flash(error, category="error")

        lang = session['lang']
        header = make_header(lang)
        return render_template("signup.jinja2", form=form, header=header)


class Logout(View):
    decorators = [login_required]

    def dispatch_request(self):
        current_app.logger.info(f"Logout utente {current_user.username}")
        logout_user()
        return redirect(url_for('start'))


auth_bp.add_url_rule("login", view_func=Login.as_view("login"))
auth_bp.add_url_rule("signup", view_func=SignUp.as_view("signup"))
auth_bp.add_url_rule("logout", view_func=Logout.as_view("logout"))
