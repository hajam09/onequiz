from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from core.models import Question
from core.models import Quiz
from core.models import QuizAttempt
from core.models import Response
from core.models import Result
from core.models import Subject


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
        super(QuizAttemptAdminForm, self).__init__(*args, **kwargs)
        # self.fields['quiz'].choices = [
        #     (i.id, f"{i.id} - {i.name} - {i.subject.name}") for i in Quiz.objects.all().select_related('subject')
        # ]

    def save(self, commit=True):
        quiz = super(QuizAttemptAdminForm, self).save(commit=False)
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
        super(QuizAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        self.save_m2m()
        return quiz


class QuizAttemptAdmin(admin.ModelAdmin):
    form = QuizAttemptAdminForm


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm


admin.site.register(Question)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(Result)
admin.site.register(Subject)
admin.site.register(Response)
