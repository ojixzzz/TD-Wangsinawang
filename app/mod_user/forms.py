from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from datetime import datetime
from app.mod_user.models import User
from werkzeug.security import check_password_hash, generate_password_hash


class LoginForm(FlaskForm):
    no_hp = StringField('No. Hp', [DataRequired(message='Nomor HP wajib diisi')])
    password = PasswordField('Password', [DataRequired(message='Password wajib diisi')])


class RegisterForm(FlaskForm):
    name = StringField('Nama', [DataRequired(message='Nama wajib diisi')])
    gender = SelectField(
        'Jenis kelamin', choices=[('L', 'Pria'), ('P', 'Wanita')]
    )
    no_hp = StringField('No. Hp', [DataRequired(message='Nomor HP wajib diisi')])

    instance = None
    document_class = User

    def __init__(self, document=None, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def save(self):
        waktu = datetime.now()
        if self.instance is None:
            self.instance = self.document_class()
            created = waktu
        else:
            created = self.instance.created

        self.instance.name = self.name.data
        self.instance.gender = self.gender.data
        self.instance.no_hp = self.no_hp.data
        self.instance.password = generate_password_hash("123456")
        self.instance.no_coupon = User().gen_no_coupon()
        self.instance.tipe = 1

        self.instance.created = created
        self.instance.modified = waktu

        self.instance.save()
        return self.instance
