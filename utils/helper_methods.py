import datetime
import os.path
import random
import string

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from cyclone.celery_task import app
from pinterest.constants import PIN_UPLOAD_PATH
from user_account.constants import USER_PROFILE_PICTURE_PATH, USER_COVER_PICTURE_PATH


def random_string():
    return ''.join(random.choices(string.ascii_uppercase, k=10))


def update_user_profile_picture_name(instance, filename):
    upload_path = USER_PROFILE_PICTURE_PATH
    file_ext = filename.split('.')[-1]
    file_name = str(instance.user.username) + '_profile_picture_' + str(instance.user.id) + '.' + file_ext
    return os.path.join(upload_path, file_name)


def update_user_cover_picture_name(instance, filename):
    upload_path = USER_COVER_PICTURE_PATH
    file_ext = filename.split('.')[-1]
    file_name = str(instance.user.username) + '_cover_picture_' + str(instance.user.id) + '.' + file_ext
    return os.path.join(upload_path, file_name)


def update_pin_file_name(instance, filename):
    upload_path = PIN_UPLOAD_PATH
    file_ext = filename.split('.')[-1]
    random_str = random_string()
    now_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = random_str + '_pin_' + str(now_datetime) + '.' + file_ext
    return os.path.join(upload_path, file_name)

@app.task
def send_mail_to_user(subject='Test Mail', to='', body='', html_template=None, context={}):
    html_page = render_to_string(template_name=html_template, context=context)
    email = EmailMultiAlternatives(
        subject=subject,
        from_email=settings.EMAIL_HOST_USER,
        to=to,
        body=body
    )
    email.attach_alternative(content=html_page, mimetype='text/html')
    email.send()
