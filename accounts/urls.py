from django.urls import path

from accounts.views import (
    registerView,
    loginView,
    logoutView,
    activateAccountView,
    passwordForgottenView,
    passwordResetView,
    extrasView,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', registerView, name='register-view'),
    path('login/', loginView, name='login-view'),
    path('logout/', logoutView, name='logout-view'),
    path('activate-account/<encodedId>/<token>/', activateAccountView, name='activate-account-view'),
    path('password-forgotten/', passwordForgottenView, name='password-forgotten-view'),
    path('password-reset/<encodedId>/<token>/', passwordResetView, name='password-reset-view'),
    path('extras/', extrasView, name='extras-view'),
]
