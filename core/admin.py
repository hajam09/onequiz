from auditlog.registry import auditlog
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from core.models import (
    Question,
    QuizAttempt,
    Quiz,
    Response,
    Result
)


class QuizAttemptAdminForm(forms.ModelForm):
    class Meta:
        model = QuizAttempt
        exclude = []

    responses = forms.ModelMultipleChoiceField(
        queryset=Response.objects.all(),
        required=False,
        label=_('Responses'),
        widget=FilteredSelectMultiple(
            verbose_name=_('Responses'),
            is_stacked=False
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        quiz = super().save(commit=False)
        quiz.save()
        self.save_m2m()
        return quiz


class QuizAdminForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all(),
        required=False,
        label=_('Questions'),
        widget=FilteredSelectMultiple(
            verbose_name=_('Questions'),
            is_stacked=False
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        quiz = super().save(commit=False)
        quiz.save()
        self.save_m2m()
        return quiz


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    form = QuizAttemptAdminForm


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    pass


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    pass


auditlog.register(Question)
auditlog.register(Quiz)
auditlog.register(QuizAttempt)
auditlog.register(Response)
auditlog.register(Result)
