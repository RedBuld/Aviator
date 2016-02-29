# -*- coding: utf-8 -*
import json
from sqlalchemy import desc, bindparam
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel, mail, celery_all
from ..models import User, products_to_users, products_to_orders, Order, Shop, Product, Settings
from ..forms import UserForm
from ..tools import check_rank_user, check_rank
from ..modules.driver import send_order
from flask.ext.mail import Message
from ..decorators import async


order_module = Blueprint('order_module', __name__)

@order_module.route('/list')
@order_module.route('/list/<int:page>')
@login_required
def list(page=1):
    if not check_rank(2):
        return abort(403)
    per_page = 30
    orders = Order.query.filter_by(status=3).order_by(desc(Order.registered_on)).paginate(page, per_page, False)
    return render_template('order/list.html', orders=orders)

@order_module.route('/calculation', methods=['GET','POST'])
@login_required
def calculation():
    if not check_rank(3):
        return abort(403)
    drivers = User.query.filter_by(rank=1).order_by(desc(User.id)).all()
    if request.method == "POST":
        date_start = request.form['date_start']+' '+request.form['time_start']
        date_end = request.form['date_end']+' '+request.form['time_end']
        driver = (int)(request.form['driver_calc'])
        total = {}
        total['summ'] = 0
        total['counts'] = 0
        orderz = Order.query.filter(Order.registered_on>=date_start, Order.registered_on<=date_end, Order.driver_id==driver, Order.status==2).all()
        for order in orderz:
            tmp = order.get_products()
            total['summ'] += tmp['price']+tmp['delivery']
            total['counts'] += 1
        return render_template('order/calculation.html',drivers=drivers, orderz=orderz, total=total)
    return render_template('order/calculation.html',drivers=drivers)

@order_module.route('/<int:order_id>/products')
@login_required
def products(order_id):
    if not check_rank(2):
        return abort(403)
    order = Order.query.get(order_id)
    if order is None:
        return abort(404)
    if not order.status == 3 and not check_rank(5):
        return abort(404)
    return render_template('order/products.html', order=order)

@order_module.route('/active')
@order_module.route('/active/<int:page>')
@login_required
def active(page=1):
    if not check_rank(4):
        return abort(403)
    per_page = 30
    orders = Order.query.filter_by(status=1).order_by(desc(Order.registered_on)).paginate(page, per_page, False)
    drivers = User.query.filter(User.id.in_([x.driver_id for x in orders.items])).all()
    for i in orders.items:
        for j in drivers:
            i._driver = j
    return render_template('order/active.html', orders=orders)

@order_module.route('/download', methods=['GET', 'POST'])
@login_required
def download():
    if not check_rank(5):
        return abort(403)
    target = request.args.get('t') or 'day'
    if request.method == 'POST':
        if target == 'all':
            orders = Order.query.order_by(desc(Order.registered_on)).all()
        else:
            if target == 'day':
                td = relativedelta(days=1)
            elif target == 'week':
                td = relativedelta(weeks=1)
            elif target == 'month':
                td = relativedelta(months=1)
            elif target == 'year':
                td = relativedelta(years=1)
            orders = Order.query.filter(Order.registered_on>=datetime.now() - td).order_by(desc(Order.registered_on)).all()
        return render_template('order/export.html', orders=orders)
    return render_template('order/download.html', target=target)

@order_module.route('/archive')
@order_module.route('/archive/<int:page>')
@login_required
def archive(page=1):
    if not check_rank(5):
        return abort(403)
    per_page = 30
    orders = Order.query.filter_by(status=2).order_by(desc(Order.registered_on)).paginate(page, per_page, False)
    drivers = User.query.filter(User.id.in_([x.driver_id for x in orders.items])).all()
    for i in orders.items:
        for j in drivers:
            i._driver = j
    return render_template('order/archive.html', orders=orders)

@order_module.route('/<int:order_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return abort(404)
    if (check_rank(2) and order.status == 3) or check_rank(4):
        if request.method == 'POST':
            order.driver = current_user
            order.status = 2
            db.session.add(order)
            db.session.commit()
            flash(_('Order successfully deleted'), 'success')
            return redirect(request.args.get('next') or url_for('order_module.list'))
        return render_template('order/delete.html', order=order, next=request.args.get('next'))
    return abort(403)

@order_module.route('/<int:order_id>/change_driver', methods=['GET', 'POST'])
@login_required
def change_driver(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return abort(404)
    if not check_rank(2):
        return abort(403)
    if not (order.status == 1 or order.status == 3):
        return abort(403)
    if request.method == 'POST':
        d = order.driver
        if not d == None:
            ptu = db.session.query(products_to_users).filter_by(user_id=d.id).all()
            pto = db.session.query(products_to_orders).filter_by(order_id=order.id).all()
            for i in pto:
                n = True
                for j in ptu:
                    if i[0] == j[0]:
                        n = False
                        if i[2] == -j[2]:
                            s = products_to_users.delete().where(products_to_users.c.user_id==d.id).\
                                where(products_to_users.c.product_id==i[0])
                        else:
                            s = products_to_users.update().values(count=i[2]+j[2]).where(products_to_users.c.user_id==d.id).\
                                where(products_to_users.c.product_id==i[0])
                if n:
                    s = products_to_users.insert().values(count=i[2], user_id=d.id, product_id=i[0])
                db.session.execute(s)
            db.session.commit()
        send_order(order, d)
        temp_user = User.query.get(d.id)
        if Settings.query.get('pdel').value:
            pdel = Settings.query.get('pdelcost').value
            temp_user.set_bank(pdel,'plus')
        flash(_('Order\' driver successfully changed'), 'success')
        return redirect(url_for('order_module.active'),301)
    return render_template('order/change_driver.html', order=order)

@celery_all.task(name='send-mail')
def send_mail(msg):
    try:
        mail.send(msg)
    except Exception, e:
        pass

def create_order(name, address, email, phone, products):
    p = Product.query.filter(Product.id.in_(products), Product.visible==1).all()
    if p is None or p == []:
        return ''
    key_enabled = Settings.query.filter_by(name='key').first()
    c = {}
    for i in products:
        if c.get(str(i)) is None:
            c[str(i)] = 1
        else:
            c[str(i)] += 1
    for i in p:
        i._count = c[str(i.id)]
    order = Order()
    order.init(name, phone, email, address)
    db.session.add(order)
    db.session.commit()
    s = products_to_orders.insert().values(product_id=bindparam('_product_id'), order_id=bindparam('_order_id'), count=bindparam('_count'))
    db.session.execute(s, [{'_product_id': x.id, '_order_id': order.id, '_count': x._count} for x in p]) 
    db.session.commit()
    send_order(order, None)
    if key_enabled.value == '1':
        msg = Message(_('Hey! That\'s your order code from')+' '+app.config['SITE_NAME'], sender=(app.config['SITE_NAME']), recipients=[order.email])
        msg.html = order_message(order)
        send_mail.delay(msg)
    return str(order.id)

def order_message(order):
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Aviator | '''+_('Order code')+'''</title>
      <link href='http://fonts.googleapis.com/css?family=Open+Sans:300italic,400,600,700' rel='stylesheet' type='text/css'>
    </head>
    <body style="min-width:500px;height:225px;width:100%;background:#DDD;padding-top:50px;">
      <div style="font-size:14px;font-family:'Open Sans', sans-serif;padding:10px 25px 30px 25px;width:400px;margin:0px auto;border-radius:3px;background:#FFF;">
        <h3 style="font-size:16px;margin-bottom:-7px;">'''+_('Dear')+' '+order.name+'''</h3>
        <p style="margin-bottom:5px;">'''+_('It\'s your order code')+''': &nbsp;<span style="font-size:15px;font-family: Tahoma, Georgia, sans-serif;background:#777;color:#FFF;padding:3px 5px;border-radius:3px;">'''+order.key+'''</span></p>
        <span style="font-size:14px;">'''+_('Thank you for your order!')+'''</span> <a style="font-size:14px;color:#777;text-decoration:none;" href="'''+app.config['SITE_URL']+'''">'''+app.config['SITE_NAME']+'''</a>
      </div>
    </body>
    </html>
    '''

@app.context_processor
def my_utility_processor():

    def date_now(format="%d.%m.%Y %H:%M:%S"):
        return datetime.now().strftime(format)

    return dict(date_now=date_now)