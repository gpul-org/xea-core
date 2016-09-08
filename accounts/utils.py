import logging
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.contrib.auth.tokens import default_token_generator

logger = logging.getLogger(__name__)


def send_activation_mail(user):
    """
     This funcion is used to send a mail containing the activation link to the new user's email address
     :param user: The user object related to the new user account
     :return:
     """
    url = build_activation_url(user)
    username = user.username
    to_email = user.email
    body_context = {'username': username, 'host': settings.SITE_HOST, 'url': url}
    subj_template = get_template('activation_mail_subject_template.txt')
    subj = subj_template.render()
    msg_template = get_template('activation_mail_body_template.txt')
    msg = msg_template.render(body_context)
    logger.info('Sending activation mail to \n' + to_email + '\n' + msg)
    send_mail(subject=subj, message=msg,
              from_email=settings.EMAIL_HOST_USER, recipient_list=[to_email], fail_silently=False)


def get_token(user):
    token = default_token_generator.make_token(user)
    return token


def validate_token(user, token):
    is_valid = default_token_generator.check_token(user, token)
    return is_valid


def build_activation_url(user):
    upk = user.pk
    token = get_token(user)
    url = reverse('activation', kwargs={'upk': upk, 'token': token})
    return url
