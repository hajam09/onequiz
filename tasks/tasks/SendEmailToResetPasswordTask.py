from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from tasks.tasks.BaseTask import BaseTask


class SendEmailToResetPasswordTask(BaseTask):

    def run(self, *args, **kwargs):
        emailSubject = 'Request to change OneTutor Password'

        user = User.objects.get(id=args[0].get('user'))
        fullName = user.get_full_name()
        domain = args[0].get('domain')

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        prtg = PasswordResetTokenGenerator()
        url = reverse('accounts:password-reset', kwargs={'encodedId': uid, 'token': prtg.make_token(user)})

        message = """
            Hi {},
            \n
            You have recently request to change your account password.
            Please click this link below to change your account password.
            \n
            http://{}{}
            \n
            Thanks,
            The OneQuiz Team
        """.format(fullName, domain, url)

        emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [user.email])
        emailMessage.send()
