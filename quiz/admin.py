from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from quiz.models import EssayQuestion
from quiz.models import EssayResponse
from quiz.models import MultipleChoiceQuestion
from quiz.models import MultipleChoiceResponse
from quiz.models import Question
from quiz.models import Quiz
from quiz.models import QuizAttempt
from quiz.models import Result
from quiz.models import Subject
from quiz.models import TrueOrFalseQuestion
from quiz.models import TrueOrFalseResponse


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
        # if self.instance.pk:
        #     self.fields['questions'].initial = self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        # quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('name',)
    list_filter = ('subject',)
    search_fields = ('description', 'subject',)


class QuizAttemptForm(forms.ModelForm):
    class Meta:
        model = QuizAttempt
        exclude = []

    def __init__(self, *args, **kwargs):
        super(QuizAttemptForm, self).__init__(*args, **kwargs)
        self.fields['quiz'].choices = [
            (i.id, f"{i.id} - {i.name} - {i.subject.name}") for i in Quiz.objects.all().select_related('subject')
        ]


class QuizAttemptAdmin(admin.ModelAdmin):
    form = QuizAttemptForm


admin.site.register(Subject)
admin.site.register(EssayQuestion)
admin.site.register(MultipleChoiceQuestion)
admin.site.register(TrueOrFalseQuestion)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Result)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(EssayResponse)
admin.site.register(MultipleChoiceResponse)
admin.site.register(TrueOrFalseResponse)
