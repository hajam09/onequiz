from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.core.signing import TimestampSigner
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from tasks.tasks.BaseTask import BaseTask


class SendEmailToVerifyNewEmailTask(BaseTask):

    def run(self, *args, **kwargs):
        emailSubject = 'Confirm your new OneQuiz email address'

        user = User.objects.get(id=args[0].get('user'))
        fullName = user.get_full_name()
        domain = args[0].get('domain')
        newEmail = args[0].get('newEmail')

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        prtg = PasswordResetTokenGenerator()
        signer = TimestampSigner()
        signedEmail = signer.sign(newEmail)
        url = reverse('accounts:verify-new-email', kwargs={'encodedId': uid, 'token': prtg.make_token(user)})

        message = """
            Hi {},
            \n
            We received a request to change the email address on your OneQuiz account.
            Please click the link below to confirm your new email address.
            \n
            http://{}{}?email={}
            \n
            Thanks,
            The OneQuiz Team
        """.format(fullName, domain, url, signedEmail)

        emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [newEmail])
        emailMessage.send()
