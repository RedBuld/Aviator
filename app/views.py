from time import time
from flask import make_response, send_from_directory, Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from app import app, babel, thumb
from app.models import User, Shop
from app.forms import LoginForm, UserForm, ShopForm
from app.modules.user import user_module
from app.modules.shop import shop_module
from app.modules.category import category_module
from app.modules.product import product_module
from app.modules.driver import driver_module
from app.modules.upload import upload_module
from app.modules.market import market_module
from app.modules.order import order_module
from app.modules.contacts import contacts_module
from app.modules.settings import settings_module

# @app.route('/media/<regex("([\w\d_/-]+)?.(?:jpe?g|gif|png)"):filename>')
@app.route('/media/<path:filename>')
def media_file(filename):
    return send_from_directory(app.config['MEDIA_FOLDER'], filename)

@babel.localeselector
def get_locale():
    if 'locale' not in session:
        session['locale'] = 'ru'
    if current_user.is_authenticated():
        # print current_user.locale
        session['locale'] = current_user.locale
    return session['locale']


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        logout_user()
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user, remember = form.remember_me)
            return redirect(request.args.get('next') or url_for('index'))
    return render_template('auth/login.html', form=form)


@app.route('/logout')
def logout():
    if current_user.is_authenticated():
        logout_user()
    return redirect(url_for('login'))


# /*-------------------------------------------------------------------------*/


@app.route('/admin')
@login_required
def index():
    if current_user.rank == 1:
        return redirect(url_for('driver_module.orders'))
    return redirect(url_for('order_module.list'))


@app.route('/admin/toggle_help')
@login_required
def toggle_help():
    response = make_response(redirect(request.args.get('next') or url_for('index')))
    if request.cookies.get('help-cont') is None or request.cookies.get('help-cont') == '':
        response.set_cookie('help-cont', 'remove', time() + (2 * 365 * 24 * 60 * 60))
    else:
        response.set_cookie('help-cont', '', time() + (2 * 365 * 24 * 60 * 60))
    return response

app.register_blueprint(user_module, url_prefix='/admin/user')
app.register_blueprint(shop_module, url_prefix='/admin/shop')
app.register_blueprint(category_module, url_prefix='/admin/category')
app.register_blueprint(product_module, url_prefix='/admin/product')
app.register_blueprint(order_module, url_prefix='/admin/order')
app.register_blueprint(contacts_module, url_prefix='/admin/contacts')
app.register_blueprint(settings_module, url_prefix='/admin/settings')

app.register_blueprint(driver_module, url_prefix='/driver')

app.register_blueprint(upload_module, url_prefix='/admin/upload')

app.register_blueprint(market_module, url_prefix='')
