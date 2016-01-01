# from flask import render_template, redirect, abort, g, session, request, flash, url_for, session, Flask
# from flask.ext.login import login_user, logout_user, current_user, login_required
# from flask.ext.admin import BaseView, expose
# from flask.ext.admin.contrib.sqla import ModelView
# from app import app, db, admin
# from app.models import User


# class MyView(ModelView):
#     def is_accessible(self):
#         if not current_user.is_authenticated():
#             return abort(403)
#         return True


# admin.add_view(MyView(User, db.session))


# /*-------------------------------------------------------------------------*/