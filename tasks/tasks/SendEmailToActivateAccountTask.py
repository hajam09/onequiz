from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from tasks.tasks.BaseTask import BaseTask


class SendEmailToActivateAccountTask(BaseTask):

    def run(self, *args, **kwargs):
        emailSubject = 'Activate your OneQuiz Account'

        user = User.objects.get(id=args[0].get('user'))
        fullName = user.get_full_name()
        domain = args[0].get('domain')

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        prtg = PasswordResetTokenGenerator()
        url = reverse('accounts:activate-account', kwargs={'encodedId': uid, 'token': prtg.make_token(user)})

        message = """
            Hi {},
            \n
            Welcome to OneQuiz, thank you for your joining our service.
            We have created an account for you to unlock more features.
            \n
            please click this link below to verify your account
            http://{}{}
            \n
            Thanks,
            The OneQuiz Team
        """.format(fullName, domain, url)

        emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [user.email])
        emailMessage.send()
