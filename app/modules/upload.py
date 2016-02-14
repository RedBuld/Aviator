import os
from werkzeug import secure_filename
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel
from ..models import Upload, Settings
from ..forms import UploadForm, UploadLogoForm, UploadAboutForm
from ..tools import check_rank_user, check_rank, get_filename, remove_img, remove_logo, remove_about


upload_module = Blueprint('upload_module', __name__)

@upload_module.route('/image', methods=['GET', 'POST'])
@login_required
def image():
    if not check_rank(3):
        return abort(403)
    filename = None
    form = UploadForm() 
    if request.method == 'POST':
        u = Upload.query.filter(Upload.registered_on <= datetime.now() - timedelta(minutes=30)).all()
        for i in u:
            try:
                remove_img(i.url)
            except Exception, e:
                pass
            db.session.delete(i)
        if form.validate_img():
            filename = get_filename(app.config['UPLOADS_FOLDER'], form.img.data.filename)
            form.img.data.save(app.config['UPLOADS_FOLDER'] + '/' + filename)
            u2 = Upload()
            u2.init(filename)
            db.session.add(u2)
            db.session.commit()
            return redirect(url_for('upload_module.image', path=filename, absolute_path='/uploads/images/'+filename))
        db.session.commit()
    return render_template('upload/image.html', form=form, filename=request.args.get('path'))

@upload_module.route('/logo', methods=['GET', 'POST'])
@login_required
def logo():
    if not check_rank(3):
        return abort(403)
    filename = 'logo.png'
    zpath = get_filename(app.config['LOGO_FOLDER'], 'logo.png')
    form = UploadLogoForm() 
    if request.method == 'POST':
        try:
            remove_logo()
        except Exception, e:
            pass
        if form.validate_img():
            form.img.data.save(app.config['LOGO_FOLDER']+'/'+filename)
            return redirect(url_for('upload_module.logo', path=zpath, absolute_path='/assets/market/image/'+filename))
    return render_template('upload/logo.html', form=form, filename=request.args.get('path'))

@upload_module.route('/about', methods=['GET', 'POST'])
@login_required
def about():
    if not check_rank(3):
        return abort(403)
    filename = None
    form = UploadAboutForm() 
    if request.method == 'POST':
        try:
            tmp = Settings.query.get('about')
            remove_about(tmp.value)
        except Exception, e:
            pass
        if form.validate_img():
            filename = get_filename(app.config['ABOUT_FOLDER'], form.img.data.filename)
            form.img.data.save(app.config['ABOUT_FOLDER']+ '/' +filename)
            about_img = Settings.query.get('about')
            if not about_img == '' and not about_img is None:
                about_img.value=filename
                Settings.update(about_img)
            else:
                about_img = Settings()
                about_img.init('about',filename)
                db.session.add(about_img)
                db.session.commit()
            return redirect(url_for('upload_module.about', path=filename, absolute_path='/assets/market/image/about-us/'+filename))
    return render_template('upload/about.html', form=form, filename=request.args.get('path'))