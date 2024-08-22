from app import db
from datetime import datetime


class User(db.Document):
    '''
    tipe:
    0 = User pasif
    1 = User aktif
    3 = Pemilik
    99 = Superuser
    100 = Blokir
    '''
    password = db.StringField()
    tipe = db.IntField(default=1)
    name = db.StringField()
    gender = db.StringField(default="")
    no_hp = db.StringField()
    no_coupon = db.IntField()

    created = db.DateTimeField(default=datetime.strptime("1945-08-17", "%Y-%m-%d"))
    modified = db.DateTimeField(default=datetime.strptime("1945-08-17", "%Y-%m-%d"))

    def gen_no_coupon(self):
        _last_user = (
            User.objects()
            .order_by("-id")
            .only("no_coupon")
            .first()
        )
        if not _last_user:
            no_coupon = 1000
        else:
            no_coupon = _last_user.no_coupon + 1

        return no_coupon
