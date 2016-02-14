from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel
from ..models import Settings
from ..tools import check_rank_user, check_rank
from ..forms import SettingsFormOne, UploadLogoForm, UploadAboutForm
from wtforms import TextAreaField

settings_module = Blueprint('settings_module', __name__)

@settings_module.route('/', methods=['GET','POST'])
@login_required
def index():
    class F(SettingsFormOne):
        pass

    if not check_rank(2):
        return abort(403)
    settings = Settings.query.all()
    sett = {}
    for i in settings:
        sett[i.name] = i.value
    for lang in app.config['LANGUAGES']:
        if 'about_q_'+lang[0] in sett:
            setattr(F, 'about_q_'+lang[0], TextAreaField(_(u'"About" quote'), default=sett['about_q_'+lang[0]]))
        else:
            setattr(F, 'about_q_'+lang[0], TextAreaField(_(u'"About" quote')))
        if 'about_text_'+lang[0] in sett:
            setattr(F, 'about_text_'+lang[0], TextAreaField(_(u'"About" text'), default=sett['about_text_'+lang[0]]))
        else:
            setattr(F, 'about_text_'+lang[0], TextAreaField(_(u'"About" text')))
        if 'address_'+lang[0] in sett:
            setattr(F, 'address_'+lang[0], TextAreaField(_(u'Address'), default=sett['address_'+lang[0]]))
        else:
            setattr(F, 'address_'+lang[0], TextAreaField(_(u'Address')))
    form = F(request.form)
    form2 = UploadLogoForm(request.form)
    form3 = UploadAboutForm(request.form)
    if request.method == "POST":
        form.upgrade(request.form)
        flash(_('Settings successfully updated'), 'success')
        return redirect(url_for('settings_module.index'))
    
    return render_template('settings/index.html', settings=sett, form=form, logo=form2, about=form3)