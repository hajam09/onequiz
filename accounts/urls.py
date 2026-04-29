from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('activate-account/<encodedId>/<token>', views.activateAccount, name='activate-account'),
    path('password-forgotten/', views.passwordForgotten, name='password-forgotten'),
    path('password-reset/<encodedId>/<token>', views.passwordReset, name='password-reset'),

    path('profile-information/', views.settingsProfileInformationView, name='profile-information-view'),
    path('change-password/', views.settingsChangePasswordView, name='change-password-view'),
    path('notifications/', views.settingsNotificationView, name='notifications-view'),
    path('activity-log/', views.settingsActivityLogView, name='activity-log-view'),
    path('account-management/', views.settingsAccountManagement, name='account-management-view'),

    # path('profile/', views.profile, name='profile-view'),
    # path('account-settings/', views.accountSettings, name='account-settings-view'),
    # path('password-settings/', views.passwordSettings, name='password-settings-view'),
    # path('security/', views.securitySettings, name='security-settings-view'),
    # path('notifications/', views.notificationSettings, name='notification-settings-view'),
    # path('email-settings/', views.emailSettings, name='email-settings-view'),
    # path('activity-log/', views.activityLog, name='activity-log-view'),
    # path('account-management/', views.accountManagement, name='account-management-view'),
    # path('email/verify/<encodedId>/<token>/', views.verifyNewEmail, name='verify-new-email'),
    # path('profile/edit/', views.editProfile, name='edit-profile'),
    # path('profile/change-avatar/', views.changeAvatar, name='change-avatar'),
    # path('password-change/', views.passwordChange, name='password-change'),
    #
    # path('email/change/', views.changeEmail, name='change-email'),
    # path('email/verify/<encodedId>/<token>/', views.verifyNewEmail, name='verify-new-email'),
    # path('deactivate/', views.deactivateAccount, name='deactivate-account'),
    # path('delete/', views.deleteAccount, name='delete-account'),
    #
    # path('email/change/', views.changeEmail, name='change-email'),
    # path('email/verify/<encodedId>/<token>/', views.verifyNewEmail, name='verify-new-email'),
    # path('deactivate/', views.deactivateAccount, name='deactivate-account'),
    # path('delete/', views.deleteAccount, name='delete-account'),
    #
    # path('activity/', views.activityLog, name='activity-log'),
    # path('request-data/', views.requestData, name='request-data'),
    path('extras/', views.extras, name='extras'),
]
