from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('activate-account/<encodedId>/<token>', views.activateAccount, name='activate-account'),
    path('password-forgotten/', views.passwordForgotten, name='password-forgotten'),
    path('password-reset/<encodedId>/<token>', views.passwordReset, name='password-reset'),
    path('account-settings', views.accountSettings, name='account-settings'),
]
