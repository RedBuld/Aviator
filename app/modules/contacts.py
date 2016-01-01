from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel, mail, celery_mail
from ..models import Contacts
from ..forms import ContactsForm
from ..tools import check_rank_user, check_rank
from flask.ext.mail import Message


contacts_module = Blueprint('contacts_module', __name__)

@contacts_module.route('/list')
@contacts_module.route('/list/<int:page>')
@login_required
def list(page=1):
    if not check_rank(2):
        return abort(403)
    per_page = 30
    query = ''
    if not request.args.get('q') is None:
        query = request.args.get('q')
        contacts = Contacts.query.filter(Contacts.name.ilike('%'+query+'%')).paginate(page, per_page, False)
    else:
        contacts = Contacts.query.paginate(page, per_page, False)
    return render_template('contacts/list.html', contacts=contacts, query=query)

@contacts_module.route('/<int:enquiry_id>/reply', methods=['GET', 'POST'])
@login_required
def reply(enquiry_id):
    contacts = Contacts.query.get(enquiry_id)
    if contacts is None:
        return abort(404)
    if not check_rank(2):
        return abort(403)
    form = ContactsForm(request.form)
    if request.method == 'POST':
        form.upgrade(contacts)
        msg = Message(_('Thanks for your feedback ')+' '+contacts.name, sender=(app.config['SITE_NAME'], app.config['SITE_NAME']), recipients=[contacts.email])
        msg.html = reply_message(contacts)
        send_mail.delay(msg)
        return redirect(url_for('category_module.list'))
    return render_template('contacts/reply.html', form=form, contacts=contacts)

@celery_mail.task(name='send-mail')
def send_mail(msg):
    try:
        mail.send(msg)
    except Exception, e:
        pass

def reply_message(reply):
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>'''+_('Thanks for your feedback')+''' | '''+app.config['SITE_NAME']+'''</title>
      <link href='http://fonts.googleapis.com/css?family=Open+Sans:300italic,400,600,700' rel='stylesheet' type='text/css'>
    </head>
    <body style="min-width:500px;width:100%;background:#DDD;padding-top:50px;padding-bottom:50px;">
      <div style="font-size:14px;font-family:'Open Sans', sans-serif;padding:10px 25px 30px 25px;width:400px;margin:0px auto;border-radius:3px;background:#FFF;">
        <h3 style="font-size:16px;margin-bottom:-7px;">'''+_('Dear')+' '+reply.name+''',</h3>
        <p style="margin-bottom:5px;">'''+reply.reply+'''</p>
        <span style="font-size:14px;">'''+_('Thanks for your feedback')+'''</span> <a style="font-size:14px;color:#777;text-decoration:none;" href="'''+app.config['SITE_URL']+'''">'''+app.config['SITE_NAME']+'''</a>
      </div>
    </body>
    </html>
    '''