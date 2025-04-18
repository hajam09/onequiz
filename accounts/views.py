from http import HTTPStatus

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from accounts.forms import LoginForm
from accounts.forms import PasswordResetForm
from accounts.forms import RegistrationForm
from onequiz.operations import emailOperations


def login(request):
    if not request.session.session_key:
        request.session.save()

    if request.method == 'POST':
        uniqueVisitorId = request.session.session_key

        if cache.get(uniqueVisitorId) is not None and cache.get(uniqueVisitorId) > 3:
            cache.set(uniqueVisitorId, cache.get(uniqueVisitorId), 600)

            messages.error(
                request, 'Your account has been temporarily locked out because of too many failed login attempts.'
            )
            return redirect('accounts:login')

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


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            newUser = form.save()
            emailOperations.sendEmailToActivateAccount(request, newUser)

            messages.info(
                request, 'We\'ve sent you an activation link. Please check your email.'
            )
            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/registration.html', context)


def logout(request):
    auth.logout(request)

    previousUrl = request.META.get('HTTP_REFERER')
    if previousUrl:
        return redirect(previousUrl)

    return redirect('accounts:login')


def activateAccount(request, encodedId, token):
    try:
        uid = force_str(urlsafe_base64_decode(encodedId))
        user = User.objects.get(pk=uid)
    except (DjangoUnicodeDecodeError, ValueError, User.DoesNotExist):
        user = None

    passwordResetTokenGenerator = PasswordResetTokenGenerator()

    if user is not None and passwordResetTokenGenerator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request,
            'Account activated successfully'
        )
        return redirect('accounts:login')

    return render(request, 'accounts/activateFailed.html', status=HTTPStatus.UNAUTHORIZED)


def passwordForgotten(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            user = None

        if user is not None:
            emailOperations.sendEmailToResetPassword(request, user)

        messages.info(
            request, 'Check your email for a password change link.'
        )

    return render(request, 'accounts/passwordForgotten.html')


def passwordReset(request, encodedId, token):
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
            return redirect('accounts:login')

    context = {
        'form': PasswordResetForm(),
    }

    TEMPLATE = 'passwordResetForm' if user is not None and verifyToken else 'activateFailed'
    return render(request, 'accounts/{}.html'.format(TEMPLATE), context)


def extras(request):
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
