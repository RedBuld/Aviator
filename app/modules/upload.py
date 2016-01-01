import os
from werkzeug import secure_filename
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, abort, g, session, request, flash, url_for, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from .. import app, db, babel
from ..models import Upload
from ..forms import UploadForm
from ..tools import check_rank_user, check_rank, get_filename


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