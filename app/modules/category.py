from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel
from ..models import Category, get_full_lenght_name, get_chained_cats
from ..forms import CategoryForm
from ..tools import check_rank_user, check_rank, remove_img


category_module = Blueprint('category_module', __name__)

@category_module.route('/list')
@category_module.route('/list/<int:page>')
@login_required
def list(page=1):
    if not check_rank(3):
        return abort(403)
    per_page = 30
    query = ''
    if not request.args.get('q') is None:
        query = request.args.get('q')
        categories = Category.query.filter(Category.name.ilike('%'+query+'%')).paginate(page, per_page, False)
    else:
        categories = Category.query.paginate(page, per_page, False)
    return render_template('category/list.html', categories=categories, query=query)

@category_module.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not check_rank(3):
        return abort(403)
    form = CategoryForm(request.form)
    if request.method == 'POST':
        rv = form.create_new()
        if rv:
            flash(_('Category successfully created'), 'success')
            return redirect(url_for('category_module.edit', category_id=form.category.id))
    form.parentid.data = 0
    return render_template('category/new.html', form=form)

@category_module.route('/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return abort(404)
    if not check_rank(3):
        return abort(403)
    form = CategoryForm(request.form)
    if request.method == 'POST':
        form.upgrade(category)
        redirect(url_for('category_module.edit', category_id=category.id))
    form.parentid.data = category.parentid
    form.parentid.choices = [(0,u'No parent category')]+[(h.id, get_full_lenght_name(h.id,h.name)) for h in Category.query.filter(Category.id.notin_(get_chained_cats(category.id,[category.id]))).all()]
    return render_template('category/edit.html', form=form, category=category)

@category_module.route('/<int:category_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return abort(404)
    if not check_rank(3):
        return abort(403)
    if request.method == 'POST':
        temp = get_chained_cats(category.id,[category.id])
        for i in temp:
            categoryz = Category.query.get(i)
            db.session.delete(categoryz)
        db.session.commit()
        flash(_('Category successfully deleted'), 'success')
        return redirect(url_for('category_module.list'))
    return render_template('category/delete.html', category=category)