from http import HTTPStatus

from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from settings.forms import ProfileUpdateForm, CustomPasswordChangeForm
from settings.models import UserNotificationSettings
from tasks.models import Task


def profileInformationView(request):
    if request.method == 'POST':
        oldEmail = request.user.email
        form = ProfileUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save(commit=False)

            if 'email' in form.changed_data:
                Task.objects.create(
                    name='SendEmailToVerifyNewEmailTask',
                    data={'domain': get_current_site(request).domain, 'user': user.pk, 'email': user.email}
                )
                user.email = oldEmail
                messages.info(
                    request,
                    'We sent a confirmation email to your new address. Please verify to complete the change.'
                )
            else:
                messages.success(
                    request,
                    'Your profile has been updated successfully.'
                )

            user.save(update_fields=['first_name', 'last_name', 'email'])
            return redirect(request.path)

    else:
        form = ProfileUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'settings/profile-information.html', context)


def verifyNewEmailView(request, encodedId, token):
    try:
        uid = force_str(urlsafe_base64_decode(encodedId))
        user = User.objects.get(pk=uid)
    except (DjangoUnicodeDecodeError, ValueError, User.DoesNotExist):
        user = None

    signedEmail = request.GET.get('email')
    signer = TimestampSigner()

    try:
        newEmail = signer.unsign(signedEmail, max_age=60 * 60 * 24) if signedEmail else None
    except (BadSignature, SignatureExpired):
        newEmail = None

    passwordResetTokenGenerator = PasswordResetTokenGenerator()
    verifyToken = user is not None and passwordResetTokenGenerator.check_token(user, token)

    if verifyToken and newEmail and not User.objects.filter(email=newEmail).exclude(pk=user.pk).exists():
        user.email = newEmail
        user.username = newEmail
        user.save(update_fields=['email', 'username'])
        messages.success(
            request, 'Your email address has been updated successfully.'
        )
        return redirect('settings:profile-information-view')

    return render(request, 'accounts/activate-failed.html', status=HTTPStatus.UNAUTHORIZED)


@login_required
def updatePasswordView(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return redirect(request.path)
    else:
        form = CustomPasswordChangeForm(user=request.user)
    context = {
        'form': form
    }
    return render(request, 'settings/update-password.html', context)


@login_required
def notificationsView(request):
    settingsObject, _ = UserNotificationSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        attributes = [
            'emailOnQuizAttemptSubmitted', 'emailOnQuizMarked', 'emailOnPasswordChanged', 'emailOnProductUpdates',
            'emailOnAccountSecurityUpdate',
        ]
        for attribute in attributes:
            setattr(settingsObject, attribute, request.POST.get(attribute) == 'on')
        settingsObject.save()
        messages.success(request, 'Your notification settings have been updated.')
        return redirect('settings:notifications-view')

    context = {
        'notificationSettings': settingsObject,
    }
    return render(request, 'settings/notifications.html', context)


@login_required
def activityLogView(request):
    context = {
    }
    return render(request, 'settings/activity-log.html', context)

@login_required
def accountManagementView(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'deactivate-account':
            request.user.is_active = False
            request.user.save(update_fields=['is_active'])
            auth.logout(request)
            messages.info(request, 'Your account has been deactivated.')
            return redirect('accounts:login-view')

        if action == 'delete-account':
            confirmation = request.POST.get('delete-account-confirmation', '').strip()
            if confirmation != 'DELETE':
                messages.error(request, 'Type DELETE to permanently delete your account.')
                return redirect('accounts:account-management-view')

            user = request.user
            auth.logout(request)
            user.delete()
            messages.success(request, 'Your account has been permanently deleted.')
            return redirect('core:index-view')

    context = {
    }
    return render(request, 'settings/account-management.html', context)
