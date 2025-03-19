import threading

from django.apps import apps
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from .models import ModelAuditLog

_user_thread_locals = threading.local()


def get_current_user():
    return getattr(_user_thread_locals, 'user', None)


def set_current_user(user):
    _user_thread_locals.user = user


class ModelChangeTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set the user from request in thread-local storage
        user = request.user if request.user.is_authenticated else None
        set_current_user(user)

        response = self.get_response(request)
        return response


class ModelChange:
    def __init__(self, field_name, field_value, field_type):
        self.field_name = field_name
        self.field_value = field_value
        self.field_type = field_type


@receiver(pre_save)
def cache_model_values_before_save(sender, instance, *args, **kwargs):
    allowed_models_to_track = ['Quiz']
    if isinstance(instance, models.Model) and instance.__class__.__name__ in allowed_models_to_track:
        app_name = instance._meta.app_label
        model_name = instance.__class__.__name__
        model_class = apps.get_model(app_name, model_name)

        if instance.pk:
            old_instance = model_class.objects.get(id=instance.pk)
            old_values = {}
            for field in old_instance._meta.fields:
                old_values[field.name] = str(getattr(old_instance, field.name))
            cache.set(f'pre-save-{app_name}-{model_name}-{instance.pk}', old_values)


@receiver(post_save)
def log_model_creation_or_update(sender, instance, created, **kwargs):
    allowed_models_to_track = ['Quiz']
    if isinstance(instance, models.Model) and instance.__class__.__name__ in allowed_models_to_track:
        model_name = instance.__class__.__name__
        action = 'CREATED' if created else 'UPDATED'

        model_audit_log = ModelAuditLog()
        model_audit_log.model_name = model_name
        model_audit_log.instance_id = instance.pk
        model_audit_log.action = action
        model_audit_log.old_values = cache.get(f'pre-save-{instance._meta.app_label}-{model_name}-{instance.pk}')

        new_values = {}
        for field in instance._meta.fields:
            new_values[field.name] = str(getattr(instance, field.name))

        fields_changed = {}
        for key, old_value in model_audit_log.old_values.items():
            new_value = new_values.get(key)
            if old_value != new_value:
                fields_changed[key] = f"{old_value} -> {new_value}"

        model_audit_log.fields_changed = fields_changed
        model_audit_log.new_values = new_values
        model_audit_log.user = get_current_user()
        model_audit_log.save()
        cache.delete(f'pre-save-{instance._meta.app_label}-{model_name}-{instance.pk}')


@receiver(pre_delete)
def log_model_deletion(sender, instance, **kwargs):
    if isinstance(instance, models.Model):
        model_name = instance.__class__.__name__
        fields_changed = {}
        old_values = {}

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(instance, field_name)
            fields_changed[field_name] = old_value
            old_values[field_name] = old_value

        # Get the user from the middleware context
        user = get_current_user()

        # Store the action in the ModelAuditLog
        # ModelAuditLog.objects.create(
        #     model_name=model_name,
        #     action='D',
        #     fields_changed=json.dumps(fields_changed),
        #     old_values=json.dumps(old_values),
        #     timestamp=now(),
        #     user=user
        # )
