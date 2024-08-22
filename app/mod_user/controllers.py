import io
import json
import qrcode
from io import BytesIO
import base64
import xlsxwriter
import datetime as datetimex
from flask import Blueprint, render_template, request, \
                  flash, g, session, redirect, url_for, abort, redirect, send_file

from flask_paginate import Pagination
from datetime import datetime, timedelta
from app.mod_user.forms import LoginForm, RegisterForm
from app.mod_user.models import User
from werkzeug.security import check_password_hash
from mongoengine.queryset.visitor import Q
from flask import make_response

mod_user = Blueprint('user', __name__, url_prefix='/')


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)


@mod_user.route('/', methods=['GET', 'POST'])
def index():
    no_hp = session.get('no_hp')
    if not no_hp:
        return redirect(url_for('user.register'))

    page = request.args.get('page')
    if not page:
        page = 1
    page = int(page)

    per_page = request.args.get('per_page')
    if not per_page:
        per_page = 10
    per_page = int(per_page)

    list_user = []
    filtercoupon = request.args.get('no_coupon', '')
    filtermonth = request.args.get('month')
    if filtermonth:
        filtermonth = int(filtermonth)
        dt_awal = datetime(datetime.now().year, filtermonth, 1, hour=0, minute=0, second=0)
        dt_akhir = last_day_of_month(datetime(datetime.now().year, filtermonth, 1, hour=23, minute=59, second=59))
        _user = User.objects.order_by("-id").filter(Q(created__gte=dt_awal) & Q(created__lte=dt_akhir))
    else:
        _user = User.objects.order_by("-id")

    if filtercoupon:
        _user = _user.filter(Q(no_coupon=int(filtercoupon)))

    _user = _user.paginate(page=page, per_page=per_page)
    for user in _user.items:
        dt_awal = datetime(datetime.now().year, datetime.now().month, 1, hour=0, minute=0, second=0)
        dt_akhir = last_day_of_month(datetime(datetime.now().year, datetime.now().month, 1, hour=23, minute=59, second=59))

        list_user.append({
            "user_id": str(user.id),
            "name": str(user.name),
            "gender": str(user.gender),
            "no_hp": str(user.no_hp),
            "tipe": str(user.tipe),
            "created": user.created,
            "no_coupon": str(user.no_coupon),
        })

    if request.args.get('export') == 'true':
        dt_now = datetime.now()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'default_date_format': 'dd/mm/yy', 'in_memory': True})
        worksheet = workbook.add_worksheet()

        worksheet.write(0, 0, 'No')
        worksheet.write(0, 1, 'No Undian')
        worksheet.write(0, 2, 'Nama')
        worksheet.write(0, 3, 'Jenis Kelamin')
        worksheet.write(0, 4, 'No Hp')
        worksheet.write(0, 5, 'Waktu mendaftar')
        row = 0
        col = 0
        for user in list_user:
            row = row + 1
            worksheet.write(row, col+0, row)
            worksheet.write(row, col+1, user['no_coupon'])
            worksheet.write(row, col+2, user['name'])
            worksheet.write(row, col+3, user['gender'])
            worksheet.write(row, col+4, user['no_hp'])
            worksheet.write(row, col+5, user['created'])

        workbook.close()
        output.seek(0)
        fileNameExport = "data_jamaah_%s.xls" % (dt_now)
        return send_file(output, download_name=fileNameExport, as_attachment=True)

    pagination = Pagination(css_framework='foundation', page=page, per_page=per_page, total=_user.total)
    data = {
        "filtercoupon": filtercoupon,
        "pagination": pagination,
        "list_user": list_user,
        "current_month": datetime.now().month
    }
    return render_template("user/user.html", data=data)


@mod_user.route('/login', methods=['GET', 'POST'])
def login():
    data = {}
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(no_hp=form.no_hp.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.tipe == 3:
                session['no_hp'] = user.no_hp
                return redirect(url_for('user.index'))
            else:
                flash('Anda tidak berhak mengakses halaman ini.', 'error')
        else:
            flash('no. hp atau password salah', 'error')

    return render_template("user/login.html", data=data, form=form)


@mod_user.route('/register', methods=['GET', 'POST'])
def register():
    data = {}
    form = RegisterForm()

    name = form.name.data
    gender = form.gender.data
    no_hp = form.no_hp.data

    sessi_no_coupon = session.get('no_coupon')
    if sessi_no_coupon:
        return redirect(url_for('user.registerSuccess'))

    if request.method == 'POST':
        if name and no_hp and gender:
            user = User.objects(no_hp=no_hp).first()
            if not user:
                _user = form.save()
                session['no_coupon'] = str(_user.no_coupon)
                flash('Berhasil disimpan', 'success')
                return redirect(url_for('user.registerSuccess'))
            else:
                session['no_coupon'] = str(user.no_coupon)
                flash('No. Telpon Sudah terdaftar', 'error')
                return redirect(url_for('user.registerSuccess'))
        else:
            flash('Error : Coba lagi, silakan isi semua pilihan dengan benar', 'error')

    response = make_response(render_template("user/register.html", data=data, form=form))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@mod_user.route('/register/success', methods=['GET', 'POST'])
def registerSuccess():
    sessi_no_coupon = session.get('no_coupon')
    if not sessi_no_coupon:
        return redirect(url_for('user.register'))

    qr_image = qrcode.make(sessi_no_coupon)
    buffer = BytesIO()
    qr_image.save(buffer)
    byte_img = buffer.getvalue()
    base64_encoded = base64.b64encode(byte_img).decode("utf-8")

    data = {
        "no_coupon": str(sessi_no_coupon),
        "qr_code": base64_encoded,
    }
    return render_template("user/register_success.html", data=data)


@mod_user.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('user.login'))
