from datetime import date


def allowed_file_image(filename):
    ALLOWED_EXTENSION = set(['png','jpg','jpeg'])
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSION


def string_date(value):
    year = value.year
    month = "%02d" % value.month
    day = "%02d" % value.day
    result = "{}-{}-{}".format(year, month, day)
    return result


def calculateAge(birthDate):
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 
    return age
