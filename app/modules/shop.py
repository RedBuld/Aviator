from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, babel, db
from ..models import Shop
from ..forms import ShopForm
from ..tools import check_rank_user, check_rank


shop_module = Blueprint('shop_module', __name__)

@shop_module.route('/list')
@shop_module.route('/list/<int:page>')
@login_required
def list(page=1):
    if not check_rank(4):
        return abort(403)
    per_page = 30
    query = ''
    if not request.args.get('q') is None:
        query = request.args.get('q')
        shops = Shop.query.filter(Shop.name.ilike('%'+query+'%')).paginate(page, per_page, False)
    else:
        shops = Shop.query.paginate(page, per_page, False)
    return render_template('shop/list.html', shops=shops, query=query)

@shop_module.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not check_rank(4):
        return abort(403)
    form = ShopForm(request.form)
    if request.method == 'POST':
        rv = form.create_new()
        if rv:
            flash(_('Shop successfully created'), 'success')
            return redirect(url_for('shop_module.edit', shop_id=form.shop.id))
    return render_template('shop/new.html', form=form)

@shop_module.route('/<int:shop_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(shop_id):
    shop = Shop.query.get(shop_id)
    if shop is None:
        return abort(404)
    if not check_rank(4):
        return abort(403)
    form = ShopForm(request.form)
    if request.method == 'POST':
        form.upgrade(shop)
    return render_template('shop/edit.html', form=form, shop=shop)

@shop_module.route('/<int:shop_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(shop_id):
    shop = Shop.query.get(shop_id)
    if shop is None:
        return abort(404)
    if not check_rank(4):
        return abort(403)
    if request.method == 'POST':
        db.session.delete(shop)
        db.session.commit()
        flash(_('Shop successfully deleted'), 'success')
        return redirect(url_for('shop_module.list'))
    return render_template('shop/delete.html', shop=shop)