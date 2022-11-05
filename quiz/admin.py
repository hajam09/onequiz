from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from quiz.models import Answer
from quiz.models import EssayQuestion
from quiz.models import MultipleChoiceQuestion
from quiz.models import Question
from quiz.models import Quiz
from quiz.models import Result
from quiz.models import Subject
from quiz.models import Topic
from quiz.models import TrueOfFalseQuestion


class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdminForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(
            verbose_name=_("Questions"),
            is_stacked=False)
    )

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('name', 'topic',)
    list_filter = ('topic',)
    search_fields = ('description', 'topic',)


class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]


admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(EssayQuestion)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
admin.site.register(TrueOfFalseQuestion)
admin.site.register(Answer)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Result)
