from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel
from ..models import User, Product, Category
from ..forms import UserForm
from ..tools import check_rank_user, check_rank


user_module = Blueprint('user_module', __name__)

@user_module.route('/change_language')
@user_module.route('/change_language/<string:lang>')
@login_required
def change_language(lang=''):
    if not lang == '':
        for i in app.config['LANGUAGES']:
            if i[0] == lang:
                current_user.locale = lang
                db.session.add(current_user)
                db.session.commit()
                if 'locale' not in session:
                    session['locale'] = lang
                session['locale'] = lang
                return redirect(request.args.get('next') or url_for('index'))
        return abort(404)
    return render_template('user/change_language.html', next=(request.args.get('next') or url_for('index')))

@user_module.route('/list')
@user_module.route('/list/<int:page>')
@login_required
def list(page=1):
    if not check_rank(3):
        return abort(403)
    per_page = 30
    query = ''
    if not request.args.get('q') is None:
        query = request.args.get('q') 
        users = User.query.filter(User.rank<5, User.username.ilike('%'+query+'%'), User.rank<current_user.rank).paginate(page, per_page, False)
    else:
        users = User.query.filter(User.rank<5, User.rank<current_user.rank).paginate(page, per_page, False)
    return render_template('user/list.html', users=users, query=query)

@user_module.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not check_rank(3):
        return abort(403)
    form = UserForm(request.form)
    if request.method == 'POST':
        rv = form.create_new()
        if rv:
            flash(_('User successfully created'), 'success')
            return redirect(url_for('user_module.edit', user_id=form.user.id))
    return render_template('user/new.html', form=form)

@user_module.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    user = User.query.get(user_id)
    if user is None:
        return abort(404)
    if not check_rank_user(user.rank):
        return abort(403)
    form = UserForm(request.form)
    if request.method == 'POST':
        if str(request.args.get('password')) == '1':
            form.upgrade_password(user)
        else:
            form.upgrade(user)
    return render_template('user/edit.html', form=form, user=user)

@user_module.route('/<int:user_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(user_id):
    user = User.query.get(user_id)
    if user is None:
        return abort(404)
    if not check_rank_user(user.rank):
        return abort(403)
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash(_('User successfully deleted'), 'success')
        return redirect(url_for('user_module.list'))
    return render_template('user/delete.html', user=user)

@user_module.route('/<int:user_id>/categories')
@user_module.route('/<int:user_id>/categories/<int:page>')
@login_required
def categories(user_id, page=1):
    user = User.query.get(user_id)
    if user is None:
        return abort(404)
    if (not check_rank_user(user.rank)) or (not user.rank == 1):
        return abort(403)
    per_page = 15
    query = ''
    if not request.args.get('q') is None:
        query = request.args.get('q')
        categories = Category.query.filter(Category.name.ilike('%'+query+'%')).paginate(page, per_page, False)
    else:
        categories = Category.query.paginate(page, per_page, False)
    return render_template('user/categories.html', categories=categories, query=query, user=user)

@user_module.route('/<int:user_id>/products/<int:category_id>')
@user_module.route('/<int:user_id>/products/<int:category_id>/<int:page>')
def products(user_id, category_id, page=1):
    user = User.query.get(user_id)
    if user is None:
        return abort(404)
    if (not check_rank_user(user.rank)) or (not user.rank == 1):
        return abort(403)
    per_page = 15
    query = ''
    category = None
    if not category_id == 0:
        category = Category.query.get(category_id)
        if category is None:
            return abort(404)
        if not request.args.get('q') is None:
            query = request.args.get('q')
            products = Product.query.filter(Product.category==category, Product.visible==True, Product.name.ilike('%'+query+'%')).paginate(page, per_page, False)
        else:
            products = Product.query.filter(Product.category==category, Product.visible==True).paginate(page, per_page, False)
    else:
        if not request.args.get('q') is None:
            query = request.args.get('q')
            products = Product.query.filter(Product.name.ilike('%'+query+'%'), Product.visible==True).paginate(page, per_page, False)
        else:
            products = Product.query.filter(Product.visible==True).paginate(page, per_page, False)
    return render_template('user/products.html', products=products, query=query, user=user, category=category)

@user_module.route('/<int:user_id>/add_product/<int:product_id>')
@login_required
def add_product(user_id, product_id):
    user = User.query.get(user_id)
    if user is None:
        return abort(404)
    if (not check_rank_user(user.rank)) or (not user.rank == 1):
        return abort(403)
    product = Product.query.get(product_id)
    if product is None:
        return abort(404)
    user.add_product(product_id)
    return redirect(url_for('user_module.edit', user_id=user.id, t='products'))

@user_module.route('/<int:user_id>/remove_product/<int:product_id>')
@login_required
def remove_product(user_id, product_id):
    user = User.query.get(user_id)
    if user is None:
        return abort(404)
    if (not check_rank_user(user.rank)) or (not user.rank == 1):
        return abort(403)
    product = Product.query.get(product_id)
    if product is None:
        return abort(404)
    user.remove_product(product_id)
    return redirect(url_for('user_module.edit', user_id=user.id, t='products'))

@user_module.route('/<int:user_id>/replenish_balance', methods=['GET', 'POST'])
@login_required
def replenish_balance(user_id):
    user = User.query.get(user_id)
    if user is None:
        return abort(404)
    if not check_rank_user(user.rank):
        return abort(403)
    if request.method == 'POST':
        user.set_bank(request.form['amount'],request.form['type'])
        return redirect(url_for('user_module.edit', user_id=user.id, t='products'))
    form = UserForm(request.form)
    return render_template('user/replenish.html', form=form, user=user)