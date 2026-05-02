from django.urls import path

from settings.views import (
    profileInformationView,
    verifyNewEmailView,
    updatePasswordView,
    accountManagementView,
    activityLogView,
    notificationsView,
)

app_name = 'settings'

urlpatterns = [
    path('profile-information/', profileInformationView, name='profile-information-view'),
    path('verify-new-email/<encodedId>/<token>/', verifyNewEmailView, name='verify-new-email-view'),
    path('update-password/', updatePasswordView, name='update-password-view'),
    path('notifications/', notificationsView, name='notifications-view'),
    path('activity-log/', activityLogView, name='activity-log-view'),
    path('account-management/', accountManagementView, name='account-management-view'),
]
