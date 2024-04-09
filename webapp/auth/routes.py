from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
import sqlalchemy as sa
from webapp import db
from webapp.auth import bp
from webapp.auth.forms import LoginForm, RegistrationForm
# ResetPasswordRequestForm, ResetPasswordForm
from webapp.models import User
from urllib.parse import urlsplit

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.musicapp'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.musicapp')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.musicapp'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.musicapp'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)