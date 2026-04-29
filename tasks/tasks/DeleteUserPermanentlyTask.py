from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from tasks.tasks.BaseTask import BaseTask


class DeleteUserPermanentlyTask(BaseTask):

    def run(self, *args, **kwargs):
        user = get_object_or_404(User, id=args[0].get('id'))
        user.is_active = False
        user.set_unusable_password()
        user.username = f'deleted_user_{user.pk}'
        user.first_name = 'deleted'
        user.last_name = 'deleted'
        user.email = f'deleted'
        user.save()
