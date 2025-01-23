from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, session
from flask.views import View
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from wtforms.validators import ValidationError
from ..models import Users, Tour
from .forms import LogInForm, SignUpForm, ResetPasswordForm, LostPasswordForm
from .. import db, mail
from ..utils import make_header


auth_bp = Blueprint('auth_bp', __name__,
                    url_prefix='/auth',
                    static_folder='static',
                    template_folder='templates'
                    )


def send_mail(recipient, user):
    msg = Message()
    msg.subject = 'Reset password'
    msg.sender = ['angelo', 'apozzi53@virgilio.it']
    msg.recipients =[recipient]
    url = f"https://foreverwalk.ddns.net{url_for('auth_bp.reset_password', user=user)}"
    msg.html = render_template('message.jinja2', url=url)

    mail.send(msg)

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
            session['_username'] = username
            if user.is_admin:
                session['tours'] = db.session.execute(db.select(func.count(Tour.id))).scalar()
            else:
                session['tours'] = len(user.tours)
            current_app.session_interface.regenerate(session)
            current_app.logger.info(f"Login utente {username}")
            return redirect(url_for('start'))

        # lang = session['lang']
        header = make_header()
        return render_template("login.jinja2", form=form, header=header)


class SignUp(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        form = SignUpForm()

        if form.validate_on_submit():
            username = request.form.get('username')
            password = request.form.get('password')
            passwd = request.form.get('vfy_password')
            email = request.form.get('email')
            error = None

            if not username:
                error = _('il campo "username" è obbligatorio')
            elif not password:
                error = _('Il campo "password" è obbligatorio')
            elif not email:
                error = _('Il campo "e-mail" è obbligatorio')

            if password != passwd :
                error = _('Le password non coincidono')

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

        errors = []
        if form.password.errors:
            for error in form.password.errors:
                if error not in errors:
                    errors.append(error)

            flash(error, category="error")
        # lang = session['lang']
        header = make_header()
        return render_template("signup.jinja2", form=form, header=header)


class Logout(View):
    decorators = [login_required]

    def dispatch_request(self):
        current_app.logger.info(f"Logout utente {current_user.username}")
        logout_user()
        session.pop('_username')
        session.pop('tours')
        if not db.session.get(Tour, session['trip']).is_visible:
            session.pop('trip')
        return redirect(url_for('start'))


class LostPassword(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        form = LostPasswordForm()
        # lang = session['lang']
        header = make_header()

        if form.validate_on_submit():
            username = request.form.get('username')
            user = db.session.execute(db.select(Users).where(Users.username == username)).scalar()
            if not user:
                flash(_('Utente sconosciuto'), category='warning')
                return render_template("lost_password.jinja2", form=form, header=header)

            send_mail(user.email, user.id)
            name, domain = user.email.split('@')
            name = f"{name[:3]}....{name[-2:]}"
            email = f"{name}@{domain}"

            return render_template("info_mail_sent.jinja2", email=email, header=header)

        return render_template("lost_password.jinja2", form=form, header=header)


class ResetPassword(View):
    methods = ['GET', 'POST']

    def dispatch_request(self, user):
        form = ResetPasswordForm()

        if form.validate_on_submit():
            password = request.form.get('new_password')
            passwd = request.form.get('vfy_password')

            user = db.session.get(Users, user)
            user.password = generate_password_hash(password)
            db.session.commit()

            return render_template("info_passwd_changed.jinja2")

        errors = []
        if form.new_password.errors:
            for error in form.new_password.errors:
                if error not in errors:
                    errors.append(error)

            flash(error, category="error")
        # lang = session['lang']
        header = make_header()
        return render_template("reset_password.jinja2", form=form, header=header)


auth_bp.add_url_rule("login", view_func=Login.as_view("login"))
auth_bp.add_url_rule("signup", view_func=SignUp.as_view("signup"))
auth_bp.add_url_rule("logout", view_func=Logout.as_view("logout"))
auth_bp.add_url_rule("lost_password", view_func=LostPassword.as_view("lost_passwd"))
auth_bp.add_url_rule("reset_password/<int:user>", view_func=ResetPassword.as_view("reset_password"))
