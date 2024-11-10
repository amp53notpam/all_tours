from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, session
from flask.views import View
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from wtforms.validators import ValidationError
from ..models import Admin
from .forms import LogInForm
from .. import db
from ..utils import make_header


auth_bp = Blueprint('auth_bp', __name__,
                    url_prefix='/auth',
                    static_folder='static',
                    template_folder='templates'
                    )


# @auth_bp.route('/login', methods=['GET', 'POST'])
class Login(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        form = LogInForm()

        if form.validate_on_submit():
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            user = db.session.execute(db.select(Admin).where(Admin.email == email)).first()

            if not user or not check_password_hash(user.Admin.password, password):
                flash('Wrong e-mail or password. Try again...', category='error')
                return redirect(url_for('auth_bp.login'))
            login_user(user.Admin, remember=remember)
            current_app.logger.info(f"Login utente {email}")
            return redirect(url_for('start'))

        if session['lang'] == 'it':
            header = make_header('it')
            return render_template("login.jinja2", form=form, header=header)
        else:
            header = make_header('en')
            return render_template("login_en.jinja2", form=form, header=header)


class Logout(View):
    decorators = [login_required]

    def dispatch_request(self):
        current_app.logger.info(f"Logout utente {current_user.email}")
        logout_user()
        return redirect(url_for('start'))


auth_bp.add_url_rule("login", view_func=Login.as_view("login"))
auth_bp.add_url_rule("logout", view_func=Logout.as_view("logout"))
