# -*- coding: utf-8 -*-
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
from app import app, db, babel
from wtforms import TextAreaField, ValidationError, Form, BooleanField, IntegerField, TextField, PasswordField, SelectField, validators
from flask_wtf.file import FileAllowed, FileRequired, FileField
from flask_wtf import Form, RecaptchaField
import hashlib
from flask.ext.login import current_user
from app.models import User, Shop, Category, Product, Upload, Settings, get_full_lenght_name, get_chained_cats
from app.tools import remove_img, check_img

class LoginForm(Form):
    email = TextField(u'Email', [
        validators.Length(min=4, max=50),
        validators.Required()
    ])
    password = PasswordField(_(u'New Password'), [
        validators.Length(max=250),
        validators.Required()
    ])
    remember_me = BooleanField(_(u'Remember Me'))

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None
        self.email.label.text = _(u'Email')
        self.password.label.text = _(u'Password')
        self.remember_me.label.text = _(u'Remember Me')

    def validate_on_submit(self):
        rv = Form.validate(self)
        if not rv:
            return False
        m = hashlib.md5()
        m.update(self.password.data)
        m = m.hexdigest()
        user = User.query.filter_by(email=self.email.data, password=m[:-len(m)+250]).first()
        if user is None:
            self.email.errors.append(_(u'Email or Password is invalid.'))
            return False
        self.user = user
        return True


# /*-------------------------------------------------------------------------*/


def user_validate_rank(form, field):
    b = True
    for rank in app.config['RANKS']:
        if rank[0] == field.data:
            b = False
            if current_user.rank < rank[2]:
                raise ValidationError(_(u'You do not have enough rights.'))
    if b:
        raise ValidationError(_(u'No rank with id ') + field.data)

def user_validate_password(form, field):
    if not field.data == form.password.data:
        raise ValidationError(_(u'Passwords do not match.'))

class ReplenishForm(Form):
    amount = IntegerField(_(u'Amount'), [
        validators.NumberRange(min=0, max=100000),
        validators.Required()
    ])
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.amount.label.text = _(u'Amount')
        

class UserForm(Form):
    name = TextField(_(u'Name'), [
        validators.Length(min=2, max=250),
        validators.Required()
    ])
    email = TextField(_(u'Email'), [
        validators.Length(min=4, max=100),
        validators.Required()
    ])
    password = PasswordField(_(u'Password'), [
        validators.Length(max=250),
        validators.Required()
    ])
    password2 = PasswordField(_(u'Repeat Password'), [
        validators.Length(max=250),
        validators.Required(),
        user_validate_password
    ])
    lang = SelectField(_(u'Language'), choices=app.config['LANGUAGES'])
    rank = IntegerField(_(u'Rank'), [
        validators.NumberRange(min=1, max=10),
        validators.Required(),
        user_validate_rank
    ])
    phone = TextField(_(u'Phone'), [])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None
        self.name.label.text = _(u'Name')
        self.email.label.text = _(u'Email')
        self.password.label.text = _(u'Password')
        self.password2.label.text = _(u'Repeat Password')
        self.lang.label.text = _(u'Language')
        self.rank.label.text = _(u'Rank')
        self.phone.label.text = _(u'Phone')

    def create_new(self):
        rv = Form.validate(self)
        if rv:
            u = User.query.filter_by(email=str(self.email.data).lower()).first()
            if not u is None:
                self.email.errors.appen(_(u'This email is already in use'))
                return False
            user = User()
            user.init(self.name.data, self.password.data, self.email.data, self.lang.data, self.rank.data, self.phone.data)
            db.session.add(user)
            db.session.commit()
            self.user = user
            return True
        return False

    def upgrade(self, user):
        r1 = self.name.validate(self)
        r2 = self.email.validate(self)
        r3 = self.lang.validate(self)
        r4 = self.rank.validate(self)
        if r1 and r2 and r3 and r4:
            u = User.query.filter_by(email=str(self.email.data).lower()).first()
            if (not u == user) and (not u is None):
                self.email.errors.appen(_(u'This email is already in use'))
                return False
            user.username = self.name.data
            user.set_email(self.email.data)
            user.lang = self.lang.data
            user.rank = self.rank.data
            user.set_phone(self.phone.data)
            db.session.add(user)
            db.session.commit()
            self.user = user
            return True
        return False

    def upgrade_password(self, user):
        r1 = self.password.validate(self)
        r2 = self.password2.validate(self)
        if r1 and r2:
            user.set_password(self.password.data)
            db.session.add(user)
            db.session.commit()
            self.user = user
            return True
        return False


class ShopForm(Form):
    name = TextField(_(u'Shop Name'), [
        validators.Length(min=2, max=250),
        validators.Required()
    ])
    address = TextField(_(u'Address'), [
        validators.Length(min=4, max=250),
        validators.Required()
    ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.shop = None
        self.name.label.text = _(u'Shop Name')
        self.address.label.text = _(u'Address')

    def create_new(self):
        rv = Form.validate(self)
        if rv:
            shop = Shop()
            shop.init(self.name.data, self.address.data)
            db.session.add(shop)
            db.session.commit()
            self.shop = shop
            return True
        return False

    def upgrade(self, shop):
        rv = Form.validate(self)
        if rv:
            shop.name = self.name.data
            shop.address = self.address.data
            db.session.add(shop)
            db.session.commit()
            self.shop = shop
            return True
        return False

class CategoryForm(Form):
    name = TextField(_(u'Category Name'), [
        validators.Length(min=2, max=250),
        validators.Required()
    ])
    num = IntegerField(_(u'Position'), [
        validators.NumberRange(min=1, max=500),
        validators.Required()
    ])
    parentid = SelectField(_(u'Parent category'), coerce=int)
    visible = BooleanField(_(u'Visible'))
    paid = BooleanField(_(u'Paid delivery'))
    dcost = IntegerField(_(u'Cost of delivery'), [
        validators.NumberRange(min=0)
    ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.category = None
        self.name.label.text = _(u'Category Name')
        self.num.label.text = _(u'Position')
        self.visible.label.text = _(u'Visible')
        self.paid.label.text = _(u'Paid')
        self.dcost.label.text = _(u'Cost of delivery')
        self.parentid.label.text = _(u'Parent category')
        self.parentid.choices = [(0,u'No parent category')]+[(h.id, get_full_lenght_name(h.id,h.name)) for h in Category.query.all()]

    def create_new(self):
        rv = Form.validate(self)
        if rv:
            category = Category()
            category.init(self.name.data, self.num.data, self.parentid.data, self.visible.data, self.paid.data, self.dcost.data)
            db.session.add(category)
            db.session.commit()
            self.category = category
            return True
        return False

    def upgrade(self, category):
        r1 = self.name.validate(self)
        r2 = self.num.validate(self)
        if r1 and r2:
            category.name = self.name.data
            category.num = self.num.data
            category.parentid = self.parentid.data
            category.visible = self.visible.data
            category.paid = self.paid.data
            category.dcost = self.dcost.data
            if str(self.dcost.data) == 'None':
                category.dcost = 0
            db.session.add(category)
            db.session.query(Category).filter(Category.id.in_(get_chained_cats(category.id,[]))).update({Category.visible:self.visible.data}, synchronize_session=False)
            db.session.commit()
            self.category = category
            return True
        return False

class ContactsForm(Form):
    name = TextField(_(u'Name'), [
        validators.Length(min=2, max=250),
        validators.Required()
    ])
    reply = TextAreaField(_(u'Reply Text'), [
        validators.Length(min=2, max=1000),
        validators.Required()
    ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.contacts = None
        self.name.label.text = _(u'Name')
        self.reply.label.text = _(u'Reply Text')

    def upgrade(self, contacts):
        r1 = self.name.validate(self)
        r2 = self.reply.validate(self)
        if r1 and r2:
            contacts.name = self.name.data
            contacts.reply = self.reply.data
            db.session.add(contacts)
            db.session.commit()
            self.contacts = contacts
            return True
        return False

class ProductForm(Form):
    name = TextField(_(u'Product Name'), [
        validators.Length(min=2, max=250),
        validators.Required()
    ])
    memo = TextAreaField(_(u'Memo'), [])
    img = TextField(_(u'Image'), [
        validators.Required()
    ])
    price = IntegerField(_(u'Price'), [
        validators.NumberRange(min=0),
        validators.Required()
    ])
    category = SelectField(_(u'Category'), validators=[
        validators.Required()
    ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.product = None
        self.name.label.text = _(u'Product Name')
        self.memo.label.text = _(u'Memo')
        self.img.label.text = _(u'Image')
        self.price.label.text = _(u'Price')
        self.category.label.text = _(u'Category')
        self.category.choices = [(h.id, h.name) for h in Category.query.all()]

    def create_new(self):
        r1 = self.name.validate(self)
        r2 = self.memo.validate(self)
        r3 = self.img.validate(self)
        r4 = self.price.validate(self)
        if r1 and r2 and r3 and r4:
            category = Category.query.get(self.category.data)
            if category is None:
                self.category.errors.append(_(u'Category not found'))
                return False
            if not check_img(self.img.data):
                self.img.errors.append(_(u'Image not found'))
                return False
            product = Product()
            product.init(self.name.data, self.memo.data, self.img.data, self.price.data)
            product.category = category
            i = Upload.query.filter_by(url=self.img.data).first()
            db.session.delete(i)
            db.session.add(product)
            db.session.commit()
            self.product = product
            return True
        return False

    def upgrade(self, product):
        r1 = self.name.validate(self)
        r2 = self.memo.validate(self)
        r3 = self.img.validate(self)
        r4 = self.price.validate(self)
        if r1 and r2 and r3 and r4:
            category = Category.query.get(self.category.data)
            if category is None:
                self.category.errors.append(_(u'Category not found'))
                return False
            product.category = category
            product.name = self.name.data
            product.memo = self.memo.data
            if not self.img.data == '' and not self.img.data is None:
                if check_img(self.img.data):
                    if not product.img == self.img.data:
                        remove_img(product.img)
                        i = Upload.query.filter_by(url=self.img.data).first()
                        db.session.delete(i)
                    product.img = self.img.data
            product.price = self.price.data
            db.session.add(product)
            db.session.commit()
            self.product = product
            return True
        return False

class UploadForm(Form):
    img = FileField(_(u'Image'), validators=[
        FileRequired(),
        FileAllowed(app.config['IMAGES'], _(u'Images only'))
    ])

    def validate_img(self):
        return self.img.validate(self)

class UploadLogoForm(Form):
    img = FileField(_(u'Image'), validators=[
        FileRequired(),
        FileAllowed(['png'], _(u'Images only'))
    ])

    def validate_img(self):
        return self.img.validate(self)

class UploadAboutForm(Form):
    img = FileField(_(u'Image'), validators=[
        FileRequired(),
        FileAllowed(app.config['IMAGES'], _(u'Images only'))
    ])

    def validate_img(self):
        return self.img.validate(self)

class SettingsFormOne(Form):
    key = BooleanField(u'Confirmation code')
    emoney = BooleanField(u'Payment cards')
    pdel = BooleanField(u'Driver paid')
    phone = TextField(u'Phone')
    email = TextField(u'Email')
    link = TextField(u'ВКонтакте')
    pdelcost = TextField(u'Cost of order')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.key.label.text = _(u'Confirmation code')
        self.emoney.label.text = _(u'Payment cards')
        self.pdel.label.text = _(u'Driver paid')
        self.phone.label.text = _(u'Phone')
        self.email.label.text = u'Email'
        self.link.label.text = u'ВКонтакте'
        self.pdelcost.label.text = _(u'Cost of order')

    def upgrade(self, settings):
        for i in settings:
            if i in self:
                param = Settings.query.get(i)
                if param is None:
                    param = Settings()
                    param.init(i,self[i].data)
                    db.session.add(param)
                    db.session.commit()
                else:
                    param.value = self[i].data
                    Settings.update(param)
            else:
                param = Settings()
                param.init(i,self[i].data)
                db.session.add(param)
                db.session.commit()
        if not self['key'].data:
            param = Settings.query.get('key')
            param.value = 0
            Settings.update(param)
        if not self['emoney'].data:
            param = Settings.query.get('emoney')
            param.value = 0
            Settings.update(param)
        if not self['pdel'].data:
            param = Settings.query.get('pdel')
            param.value = 0
            Settings.update(param)
        return True