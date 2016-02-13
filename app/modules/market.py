# -*- coding: utf-8 -*-
import re
from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, Flask, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext, refresh
from .. import app, db, babel, thumb
from ..models import User, Product, Category, Streets, Contacts, Subscribe, Order, Settings, get_chained_cats_lvl_one, get_categories_by_cart
from order import create_order
from ..forms import UserForm
from ..tools import check_rank_user, check_rank
from sqlalchemy import asc, func
from jinja2 import evalcontextfilter, Markup, escape
import json

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

market_module = Blueprint('market_module', __name__)

#инициализация сессии
@app.before_request
def set_client_session():
    #сессия языка
    if 'locale' not in session:
        session['locale'] = 'ru'
    #сессия корзины
    if 'bag' not in session:
        session['bag']=[]
    if 'paidcats' not in session:
        session['paidcats']=[]
    if 'last' not in session:
        session['last']=[]
    if 'total' not in session:
        session['total']={}
        session['total']['counts'] = 0
        session['total']['price'] = 0
        session['total']['delivery']=0

# 404 страница
@app.errorhandler(404)
def page_not_found(e):
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    settings = Settings.query.all()
    return render_template('market/functional/error_page.html', categories_all=categories_all, settings=settings), 404
#    return redirect(url_for('market_module.index'))

#смена языка
@market_module.route('/set_locale', methods=["POST"])
def set_locale():
    nlocale = request.form['code']
    redirect_way = request.form['redirect']
    session['locale'] = nlocale
    if current_user.is_authenticated():
        current_user.locale = nlocale
        db.session.add(current_user)
        db.session.commit()
    refresh()
    return redirect(redirect_way)

#категории
@market_module.route('/', defaults={'category_name': ''})
@market_module.route('/<category_name>')
def index(category_name):
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    if category_name == '':
        category = Category.query.order_by(asc(Category.num)).filter_by(visible=1).first_or_404()
    else:
        category = Category.query.order_by(asc(Category.num)).filter(func.lower(Category.name)==func.lower(category_name)).first_or_404()
    products = Product.query.filter(Product.category_id.in_(get_chained_cats_lvl_one(category.id,[category.id])))
    settings = Settings.query.all()
    return render_template('market/index.html', categories_all=categories_all, category=category, products=products, settings=settings)

@market_module.route('/testx/')
def testx():
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    return render_template('market/testx.html', categories_all=categories_all)

#страница продукта
@market_module.route('/product/<int:product_id>')
def product(product_id):
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    product = Product.query.filter_by(id=product_id).first_or_404()
    current_category = Category.query.filter_by(id=product.category_id).first_or_404()
    settings = Settings.query.all()
    return render_template('market/product.html', product=product, categories_all=categories_all, category=current_category, settings=settings)

#обзор продукта
@market_module.route('/quickview/<int:product_id>')
def quickview(product_id):
    product = Product.query.filter_by(id=product_id).first_or_404()
    return render_template('market/quickview.html', product=product)

# основная секция
# добавление продукта в корзину
@market_module.route('/add_product/<int:product_id>/<int:counts>')
def add_product(product_id,counts):
    id = int(product_id)
    qty = int(counts)
    result = {}
    matching = [d for d in session['bag'] if d['pid'] == id]
    if matching:
        matching[0]['qty'] += qty
        session['last'] = matching[0]
        session['total']['price'] += qty*matching[0]['price']
        session['total']['counts'] += qty
    else:
        product = Product.query.filter_by(id=product_id).first()
        session["bag"].append(dict({'pid': id, 'category_id':product.category_id, 'name': product.name, 'qty': qty, 'img': thumb.thumbnail(product.img,'200x200'), 'price': product.price}))
        session['last'] = dict({'pid': id, 'category_id':product.category_id, 'name': product.name, 'qty': qty, 'img': thumb.thumbnail(product.img,'200x200'), 'price': product.price})
        session['total']['price'] += qty*product.price
        session['total']['counts'] += qty
    session['paidcats'] = get_categories_by_cart(session['bag'])
    session['total']['delivery'] = 0
    for i in session['paidcats']:
        session['total']['delivery'] = session['total']['delivery']+i['cost']
    result['result'] = 'success'
    result['last'] = session['last']
    result['total'] = session['total']
    result['success'] = '<a href="/pid'+str(id)+'">'+session['last']['name']+'</a> '+_('added to ')+'<a href="/cart">'+_('shopping cart')+'</a>'
    result['cartheader'] = ngettext('%(num)d item', '%(num)d items',session['total']['counts']) % {'num': session['total']['counts']}+' - '+str(session['total']['price']+session['total']['delivery'])+' '+_('rub.')
    return json.dumps(result)

# уменьшение кол-ва продукта в корзине
@market_module.route('/remove_product/<int:product_id>')
def remove_product(product_id):
    id = int(product_id)
    result = {}
    matching = [d for d in session['bag'] if d['pid'] == id]
    if matching:
        if matching[0]['qty'] > 1:
            matching[0]['qty'] -= 1
            session['last'] = matching[0]
            session['total']['price'] -= matching[0]['price']
            session['total']['counts'] -= 1
        else:
            delete_product(id)
        result['result'] = 'success'
    else:
        result['result'] = 'false'
    session['paidcats'] = get_categories_by_cart(session['bag'])
    session['total']['delivery'] = 0
    for i in session['paidcats']:
        session['total']['delivery'] = session['total']['delivery']+i['cost']
    result['last'] = session['last']
    result['total'] = session['total']
    result['success'] = '<a href="/pid'+str(id)+'">'+session['last']['name']+'</a> '+_('removed from ')+'<a href="/cart">'+_('shopping cart ')+'</a>'
    result['cartheader'] = ngettext('%(num)d item', '%(num)d items',session['total']['counts']) % {'num': session['total']['counts']}+' - '+str(session['total']['price']+session['total']['delivery'])+' '+_('rub.')
    return json.dumps(result)

# удаление продукта из корзины
@market_module.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    id = int(product_id)
    result = {}
    matching = [d for d in session['bag'] if d['pid'] == id]
    if matching:
        qty = matching[0]['qty']
        img = matching[0]['img']
        name = matching[0]['name']
        price = matching[0]['price']
        session['bag'].remove(matching[0])
        session['last'] = matching[0]
        session['total']['price'] -= qty*price
        session['total']['counts'] -= qty
        result['result'] = 'success'
    else:
        result['result'] = 'false'
    session['paidcats'] = get_categories_by_cart(session['bag'])
    session['total']['delivery'] = 0
    for i in session['paidcats']:
        session['total']['delivery'] = session['total']['delivery']+i['cost']
    result['last'] = session['last']
    result['total'] = session['total']
    result['success'] = '<a href="/pid'+str(id)+'">'+session['last']['name']+'</a> '+_('removed from ')+'<a href="/cart">'+_('shopping cart ')+'</a>'
    result['cartheader'] = ngettext('%(num)d item', '%(num)d items',session['total']['counts']) % {'num': session['total']['counts']}+' - '+str(session['total']['price']+session['total']['delivery'])+' '+_('rub.')
    return json.dumps(result)

# очистка корзины
@market_module.route('/clean_cart')
def clean_cart():
    session['bag']=[]
    session['last']=[]
    session['paidcats']=[]
    session['total']={}
    session['total']['counts'] = 0
    session['total']['price'] = 0
    session['total']['delivery'] = 0
    return 'true'

# мини корзина
@market_module.route('/cart_overview')
def cart_overview():
    if len(session['bag']) > 0:
        e = 1
    else:
        e = 0
    return render_template('market/cart_overview.html', products = session['bag'], total=session['total'], empty=e)

# большая корзина
@market_module.route('/cart')
def cart():
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    if len(session['bag']) > 0:
        e = 1
    else:
        e = 0
    settings = Settings.query.all()
    return render_template('market/cart.html', categories_all=categories_all, products = session['bag'], empty=e, settings=settings)

# таблица большой корзины
@market_module.route('/cartview')
def cartview():
    if len(session['bag']) > 0:
        e = 1
    else:
        e = 0
    return render_template('market/templates/cartview.html', products = session['bag'], total=session['total'], empty=e)

# заполнение данных клиента
@market_module.route('/checkout')
def checkout():
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    if len(session['bag']) > 0:
        e = 1
    else:
        e = 0
    settings = Settings.query.all()
    return render_template('market/checkout.html', categories_all=categories_all, products = session['bag'], empty=e, settings=settings)

# таблица заполнения данных клиента
@market_module.route('/checkview')
def checkview():
    if len(session['bag']) > 0:
        e = 1
    else:
        e = 0
    return render_template('market/templates/checkview.html', products = session['bag'], total=session['total'], empty=e)

# оформление заказа
@market_module.route('/order_create', methods=['POST'])
def order_create():
    name = u''+request.form['firstname']+u' '+request.form['lastname']
    email = request.form['email']
    phone = request.form['telephone']
    address = u'Вологда, '+request.form['street']+u', д.'+request.form['house']+u', кв.'+request.form['apartment']
    products = []
    for product in session['bag']:
        for i in range(int(product['qty'])):
            products.append(int(product['pid']))
    order_info = create_order(name, address, email, phone, products)
    result = {}
    if order_info == '':
        result['status'] = 'false'
    else:
        result['status'] = 'true'
        session['order_id'] = order_info
        clean_cart()
    return json.dumps(result)

# успешное оформление заказа
@market_module.route('/checkout/success')
def success():
    if 'order_id' not in session:
        abort(404)
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    order = Order.query.filter_by(id=session['order_id']).first()
    settings = Settings.query.all()
    return render_template('market/checkout_finished.html', categories_all=categories_all, order=order, settings=settings)

# дополнительные секции
# о нас
@market_module.route('/about')
def about():
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    data = {}
    settings = Settings.query.all()
    return render_template('market/about.html', categories_all=categories_all, settings=settings)

@market_module.route('/sitemap')
def sitemap():
    categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
    products_by_cat = {}
    for category in categories_all:
        products_by_cat[category.name] = Product.query.filter_by(category_id=category.id).all()
    settings = Settings.query.all()
    return render_template('market/sitemap.html', categories_all=categories_all, products_by_cat=products_by_cat, settings=settings)

# обратная связь
@market_module.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        answer = ''
        enquiry = request.form['enquiry']
        contact = Contacts()
        contact.init(name, email, enquiry)
        db.session.add(contact)
        db.session.commit()
        result = {
            'result':'success'
        }
        return json.dumps(result)
    else:
        categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
        settings = Settings.query.all()
        return render_template('market/contact.html', categories_all=categories_all, settings=settings)

# обратная связь
@market_module.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['subscribe_email']
    if not re.match('(\w+[.|\w])*@(\w+[.])*\w+',email):
        result = {
            'error': _('Incorrect Email')
        }
        return json.dumps(result)
    email_isset = Subscribe.query.filter_by(email=email).limit(1)
    if email_isset.count() == 1:
        result = {
            'error': _('You already subscribed')+'. <a href="javascript:email_unsubscribe();">'+_('Unsubscribe')+'</a>'
        }
    else:
        subscribe = Subscribe()
        subscribe.init(email)
        db.session.add(subscribe)
        db.session.commit()
        result = {
            'success':_('You have subscribed to our newsletter')
        }
    return json.dumps(result)

# обратная связь
@market_module.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    email = request.form['subscribe_email']
    if not re.match('(\w+[.|\w])*@(\w+[.])*\w+',email):
        result = {
            'error': _('Incorrect Email')
        }
        return json.dumps(result)
    email_isset = Subscribe.query.filter_by(email=email).limit(1)
    if email_isset.count() == 1:
        db.session.delete(email_isset[0])
        db.session.commit()
        result = {
            'success':_('You have unsubscribed from our newsletter')
        }
    else:
        result = {
            'success':_('You already unsubscribed')
        }
    return json.dumps(result)

@market_module.route('/get_streets')
def get_streets():
    streets = Streets.query.all()
    temp = {}
    for i in streets:
        temp[i.id] = {}
        temp[i.id]["name"] = i.name
    return json.dumps(temp)

@market_module.route('/search/', defaults={'search_string': ''}, methods={'POST','GET'})
@market_module.route('/search/<search_string>', methods={'POST','GET'})
def search(search_string):
    results = {}
    if request.method == 'POST':
        results['products'] = {}
        results['counts'] = {}
        if not search_string == '':
            search_string = search_string.lower()
            for e in search_string.split(' '):
                temp = Product.query.filter(Product.name.ilike('%' + e + '%')).all()
                for i in temp:
                    results['products'][i.id] = {}
                    results['products'][i.id]["name"] = i.name
                    results['products'][i.id]["price"] = str(i.price) +' '+ _('rub.')
                    results['products'][i.id]["img"] = thumb.thumbnail(i.img,'200x200')
            results['counts']['val'] = len(results['products'])
            results['counts']['text'] = _('Show more')
        return json.dumps(results)
    else:
        categories_all = Category.query.order_by(asc(Category.num)).filter_by(parentid=0,visible=1).all()
        settings = Settings.query.all()
        products = {}
        if not search_string == '':
            search_string = search_string.lower()
            for e in search_string.split(' '):
                products = Product.query.filter(Product.name.ilike('%' + e + '%')).all()
        return render_template('market/search.html', categories_all=categories_all, products=products, settings=settings)

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'%s<br>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

@app.context_processor
def my_utility_processor():

    def get_name(id):
        product = Product.query.filter_by(id=id)
        name = ''
        for i in product:
            name = i.name
        return name

    return dict(get_name=get_name)