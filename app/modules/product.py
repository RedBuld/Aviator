from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel
from ..models import Product, Category
from ..forms import ProductForm
from ..tools import check_rank_user, check_rank, remove_img


product_module = Blueprint('product_module', __name__)

@product_module.route('/list')
@product_module.route('/list/<int:page>')
@login_required
def list(page=1):
    if not check_rank(3):
        return abort(403)
    category_id = request.args.get('category')
    per_page = 30
    query = ''
    category = None
    if not category_id is None:
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
            products = Product.query.filter_by(visible=True).paginate(page, per_page, False)
    return render_template('product/list.html', products=products, category=category, query=query)

@product_module.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not check_rank(3):
        return abort(403)
    db.session.commit()
    form = ProductForm(request.form)
    if request.method == 'POST':
        rv = form.create_new()
        if rv:
            flash(_('Product successfully created'), 'success')
            return redirect(url_for('product_module.edit', product_id=form.product.id))
    # categories = Category.query.all()
    return render_template('product/new.html', form=form)

@product_module.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return abort(404)
    if not check_rank(3):
        return abort(403)
    if not product.visible:
        return abort(404)
    form = ProductForm(request.form)
    if request.method == 'POST':
        form.upgrade(product)
    return render_template('product/edit.html', form=form, product=product)

@product_module.route('/<int:product_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return abort(404)
    if not check_rank(3):
        return abort(403)
    if not product.visible:
        return abort(404)
    if request.method == 'POST':
        remove_img(product.img)
        product.visible = False
        product.img = ''
        db.session.add(product)
        db.session.commit()
        flash(_('Product successfully deleted'), 'success')
        return redirect(url_for('product_module.list'))
    return render_template('product/delete.html', product=product)