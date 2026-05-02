from http import HTTPStatus

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, url_has_allowed_host_and_scheme

from accounts.forms import LoginForm
from accounts.forms import PasswordResetForm
from accounts.forms import RegisterForm
from tasks.models import Task


def registerView(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Task.objects.create(
                name='SendEmailToActivateAccountTask',
                data={'domain': get_current_site(request).domain, 'user': user.pk},
            )

            messages.info(
                request, 'We\'ve sent you an activation link. Please check your email.'
            )
            return redirect('accounts:login-view')
    else:
        form = RegisterForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def loginView(request):
    if not request.session.session_key:
        request.session.save()

    if request.method == 'POST':
        uniqueVisitorId = request.session.session_key

        if cache.get(uniqueVisitorId) is not None and cache.get(uniqueVisitorId) > 3:
            cache.set(uniqueVisitorId, cache.get(uniqueVisitorId), 600)

            messages.error(
                request, 'Your account has been temporarily locked out because of too many failed login attempts.'
            )
            return redirect('accounts:login-view')

        form = LoginForm(request, request.POST)

        if form.is_valid():
            cache.delete(uniqueVisitorId)
            redirectUrl = request.GET.get('next')
            if redirectUrl:
                return redirect(redirectUrl)
            return redirect('core:index-view')

        if cache.get(uniqueVisitorId) is None:
            cache.set(uniqueVisitorId, 1)
        else:
            cache.incr(uniqueVisitorId, 1)

    else:
        form = LoginForm(request)

    context = {
        'form': form
    }
    return render(request, 'accounts/login.html', context)


def logoutView(request):
    auth.logout(request)

    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(referer, {request.get_host()}):
        return redirect(referer)

    return redirect('accounts:login-view')


def activateAccountView(request, encodedId, token):
    try:
        uid = force_str(urlsafe_base64_decode(encodedId))
        user = User.objects.get(pk=uid)
    except (DjangoUnicodeDecodeError, ValueError, User.DoesNotExist):
        user = None

    passwordResetTokenGenerator = PasswordResetTokenGenerator()

    if user is not None and passwordResetTokenGenerator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])

        messages.success(
            request,
            'Account activated successfully'
        )
        return redirect('accounts:login-view')

    return render(request, 'accounts/activate-failed.html', status=HTTPStatus.UNAUTHORIZED)


def passwordForgottenView(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            user = None

        if user is not None:
            Task.objects.create(
                name='SendEmailToResetPasswordTask',
                data={'domain': get_current_site(request).domain, 'user': user.pk},
            )

        messages.info(
            request, 'Check your email for a password change link.'
        )

    return render(request, 'accounts/password-forgotten.html')


def passwordResetView(request, encodedId, token):
    try:
        uid = force_str(urlsafe_base64_decode(encodedId))
        user = User.objects.get(pk=uid)
    except (DjangoUnicodeDecodeError, ValueError, User.DoesNotExist):
        user = None

    passwordResetTokenGenerator = PasswordResetTokenGenerator()
    verifyToken = passwordResetTokenGenerator.check_token(user, token)

    if request.method == 'POST' and user is not None and verifyToken:
        form = PasswordResetForm(request, user, request.POST)

        if form.is_valid():
            form.updatePassword()
            return redirect('accounts:login-view')

    context = {
        'form': PasswordResetForm(),
    }

    TEMPLATE = 'password-reset' if user is not None and verifyToken else 'activate-failed'
    return render(request, 'accounts/{}.html'.format(TEMPLATE), context)


def extrasView(request):
    if request.GET.get('page') == 'privacy-policy':
        template = 'accounts/privacyPolicy.html'
    elif request.GET.get('page') == 'terms-and-conditions':
        template = 'accounts/termsAndConditions.html'
    else:
        raise Http404

    return render(request, template)


def handler404(request, exception):
    return render(request, 'accounts/404.html', status=404)


def handler500(request):
    return render(request, 'accounts/500.html', status=500)
