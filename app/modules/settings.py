from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel, mail, celery_mail
from ..models import Settings
from ..tools import check_rank_user, check_rank

settings_module = Blueprint('settings_module', __name__)

@settings_module.route('/', methods=['GET','POST'])
@login_required
def index():
    if not check_rank(2):
        return abort(403)
    settings = Settings.query.all()
    if request.method == "POST":
    	for i in request.form:
    		param = Settings.query.get(i)
    		param.value = request.form[i]
    		Settings.update(param)
    	if 'key' not in request.form:
    		param = Settings.query.get('key')
    		param.value = '0'
    		Settings.update(param)
        if 'emoney' not in request.form:
            param = Settings.query.get('emoney')
            param.value = '0'
            Settings.update(param)
    	flash(_('Settings successfully updated'), 'success')
    	return redirect(url_for('settings_module.index'))
    sett = {}
    for i in settings:
        sett[i.name] = i.value
    return render_template('settings/index.html', settings=sett)