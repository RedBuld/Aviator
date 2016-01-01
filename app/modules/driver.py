import json
from datetime import datetime, timedelta
from flask import flash, Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel, celery_all
from ..models import User, products_to_users, products_to_orders, Order, Shop, Settings
from ..forms import UserForm
from ..tools import check_rank_user, check_rank


driver_module = Blueprint('driver_module', __name__)

@driver_module.route('/list')
@driver_module.route('/map')
@driver_module.route('/list/<int:page>')
@driver_module.route('/map/<int:page>')
@login_required
def list(page=1):
    if not check_rank(4):
        return abort(403)
    per_page = 15
    query = ''
    if not request.args.get('q') is None:
        query = request.args.get('q')
        drivers = User.query.filter(User.rank==1, User.username.ilike('%'+query+'%')).paginate(page, per_page, False)
    else:
        drivers = User.query.filter(User.rank==1).paginate(page, per_page, False)
    fresh_drivers = User.query.filter(User.rank==1, User.coord!=None, User.coord_date>=datetime.now() - app.config['ACTIVE_DRIVER_TIMEDELTA']).all()
    return render_template('driver/list.html', drivers=drivers, fresh_drivers=fresh_drivers, query=query)

@driver_module.route('/fresh_coord/<int:driver_id>')
@login_required
def fresh_coord(driver_id):
    if not check_rank(4):
        return abort(403)
    driver = User.query.filter(User.id==driver_id, User.rank==1).first()
    if driver is None:
        return abort(404)
    data = {"coord": driver.coord, "name": driver.username}
    return json.dumps(data)

@driver_module.route('/fresh_drivers')
@login_required
def fresh_drivers():
    if not check_rank(4):
        return abort(403)
    fresh_drivers = User.query.filter(User.rank==1, User.coord!=None, User.coord_date>=datetime.now() - timedelta(minutes=30)).all()
    data = []
    for driver in fresh_drivers:
        data.append({"id": driver.id, "name": driver.username, "phone": driver.get_phone(), "coord": driver.coord, "marker": {}})
    return json.dumps(data)

@driver_module.route('/coord', methods=['POST'])
@login_required
def coord():
    if not current_user.rank == 1:
        abort(403)
    if request.form['coord'] == None:
        abort(404)
    current_user.coord = str(request.form['coord'])
    current_user.coord_date = datetime.now()
    db.session.add(current_user)
    db.session.commit()
    return ''

@driver_module.route('/coord_get_orders')
def coord_get_orders():
    if not current_user.rank == 1:
        abort(403)
    if request.args.get('coord') == None:
        abort(404)
    current_user.coord = str(request.args.get('coord'))
    current_user.coord_date = datetime.now()
    db.session.add(current_user)
    db.session.commit()
    orders = Order.query.filter(Order.driver == current_user, Order.status <= 1).all()
    return render_template('driver/orders.html', orders=orders)

@driver_module.route('/orders')
@login_required
def orders():
    if not current_user.rank == 1:
        return abort(403)
    orders = Order.query.filter(Order.driver == current_user, Order.status <= 1).all()
    key_enabled = Settings.query.get('key')
    return render_template('driver/orders.html', orders=orders, key_enabled=key_enabled)

@driver_module.route('/order/<int:order_id>/accept')
@login_required
def order_accept(order_id):
    if not current_user.rank == 1:
        return abort(403)
    order = Order.query.get(order_id)
    if order is None:
        return abort(404)
    if not order.driver == current_user:
        return abort(403)
    rem_products_and_confirm(order, current_user)
    return redirect(url_for('driver_module.orders', t='active'))

@driver_module.route('/order/<int:order_id>/cancel')
@login_required
def order_cancel(order_id):
    if not current_user.rank == 1:
        return abort(403)
    order = Order.query.get(order_id)
    if order is None:
        return abort(404)
    if not order.driver == current_user:
        return abort(403)
    send_order(order, current_user)
    return redirect(url_for('driver_module.orders'))

@driver_module.route('/order/<int:order_id>/complete', methods=['GET', 'POST'])
@login_required
def order_complete(order_id):
    if not current_user.rank == 1:
        return abort(403)
    order = Order.query.get(order_id)
    if order is None:
        return abort(404)
    if (not order.driver == current_user) or (not order.status == 1):
        return abort(403)
    key_enabled = Settings.query.get('key').value
    if key_enabled == '0':
        order.status = 2
        db.session.add(order)
        db.session.commit()
        flash(_('Order has been successfully completed'), 'success')
        return redirect(url_for('driver_module.orders', t='active'))
    elif request.method == 'POST':
        if str(request.form['key']).upper() == order.key:
            order.status = 2
            db.session.add(order)
            db.session.commit()
            flash(_('Order has been successfully completed'), 'success')
        else:
            flash(_('The key is incorrect'), 'error')
        return redirect(url_for('driver_module.orders', t='active'))
    return render_template('driver/complete.html', order=order)

@driver_module.route('/products')
@login_required
def products():
    if not current_user.rank == 1:
        return abort(403)
    return render_template('driver/products.html', driver=current_user)

@driver_module.route('/route/<int:order_id>')
@login_required
def route(order_id):
    if not current_user.rank == 1:
        return abort(403)
    order = Order.query.get(order_id)
    if order is None:
        return abort(404)
    if not order.status == 1:
        return abort(404)
    if not order.driver == current_user:
        return abort(403)
    confirm_order(order, current_user)
    shops = Shop.query.all()
    return render_template('driver/route.html', driver=current_user, order=order, shops=shops)


@celery_all.task(name='check-order-after-send')
def check_order_after_send(order_id, re_count):
    order = Order.query.get(order_id)
    if re_count == order.re_count and order.status == 0:
        send_order(order, order.driver)


def send_order(order, user):
    const_timedelta = app.config['ACTIVE_DRIVER_TIMEDELTA']
    const_products = 1
    const_orders = 7.5
    data = {}
    data2 = {}
    products = db.session.query(products_to_orders).filter_by(order_id=order.id).all()
    order.status = 0
    d = User.query.filter(User.rank==1, User.coord!=None, User.coord_date>=(datetime.now() - const_timedelta) ).all()
    ids = [x.id for x in d]
    if ids == []:
        order.status = 3
    else:
        products2 = db.session.query(products_to_users).filter(products_to_users.c.user_id.in_(ids)).all()
        orders = Order.query.filter(Order.driver_id.in_(ids), Order.status==1).all()
        # nm = {}
        for i in products2:
            if data.get(str(i[1])) is None:
                data[str(i[1])] = []
            data[str(i[1])].append(i)
        for i in orders:
            if data2.get(str(i.driver_id)) is None:
                data2[str(i.driver_id)] = 0
            data2[str(i.driver_id)] += 1
        def sort_by_count(x):
            p = data.get(str(x.id))
            p_ball = 0
            # nm[str(x.id)] = True
            l = 0
            if not p is None:
                for i in p:
                    for j in products:
                        if str(i[0]) == str(j[0]):
                            for u in xrange(1, j[2]+1):
                                if i[2] >= u:
                                    p_ball += 1
                                # l += 1
            # if l == p_ball and not p_ball == 0:
            #     nm[str(x.id)] = False
            o = data2.get(str(x.id))
            if o is None:
                o = 0
            return p_ball*const_products - o*const_orders
        d.sort(key=sort_by_count, reverse=True)
        if len(d) == 0:
            order.status = 3
        else:
            if len(d) <= 1 and d[0] == user:
                order.status = 3
            else:
                order.driver = d[0]
                # order.need_market = nm.get(str(d[0].id))
    order.take_time = datetime.now()
    order.re_count += 1
    if order.re_count == 4:
        order.status = 3
    db.session.add(order)
    db.session.commit()
    check_order_after_send.apply_async(args=[order.id, order.re_count], countdown=120)

def confirm_order(order, user):
    p_need_market = order.need_market
    p_status = order.status
    products = db.session.query(products_to_orders).filter_by(order_id=order.id).all()
    products2 = db.session.query(products_to_users).filter(products_to_users.c.user_id == user.id).all()
    order.need_market = False
    f = True
    for i in products:
        for j in products2:
            if i[0] == j[0]:
                if j[2] < i[2]:
                    f = False
    if not f:
        order.need_market = True
    order.status = 1
    if not (order.need_market == p_need_market and order.status == p_status):
        db.session.add(order)
        db.session.commit()

def rem_products_and_confirm(order, user):
    p_need_market = order.need_market
    p_status = order.status
    products = db.session.query(products_to_orders).filter_by(order_id=order.id).all()
    products2 = db.session.query(products_to_users).filter(products_to_users.c.user_id == user.id).all()
    order.need_market = False
    f = True
    for i in products:
        for j in products2:
            if i[0] == j[0]:
                if j[2] < i[2]:
                    f = False
    if not f:
        order.need_market = True
    order.status = 1
    for j in products:
        n = True
        for i in products2:
            if i[0] == j[0]:
                n = False
                if i[2] == j[2]:
                    s = products_to_users.delete().where(products_to_users.c.user_id==current_user.id).\
                        where(products_to_users.c.product_id==i[0])
                else:
                    s = products_to_users.update().values(count=i[2]-j[2]).where(products_to_users.c.user_id==current_user.id).\
                        where(products_to_users.c.product_id==i[0])
        if n:
            s = products_to_users.insert().values(user_id=current_user.id, product_id=j[0], count=-j[2])
        db.session.execute(s)
    if not (order.need_market == p_need_market and order.status == p_status):
        db.session.add(order)
    db.session.commit()