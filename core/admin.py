from auditlog.registry import auditlog
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from core.models import (
    Question,
    QuizAttempt,
    Quiz,
    Response,
    Result
)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'url',
        'quiz_link',
        'questionType'
    ]
    list_filter = [
        'questionType'
    ]
    search_fields = [
        'id',
        'url',
        'content',
        'explanation',
        'questionType',
        'quiz__name',
        'quiz__description',
        'quiz__url',
        'quiz__subject',
        'quiz__topic',
        'quiz__difficulty'
    ]

    def quiz_link(self, question):
        if not question.quiz:
            return None

        app_label = question.quiz._meta.app_label
        model_name = question.quiz._meta.model_name
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[question.quiz.id])
        return format_html('<a href="{}">{}</a>', url, question.quiz)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'url',
        'quiz_link',
        'status'
    ]
    list_filter = [
        'status',
        'quiz'
    ]
    search_fields = [
        'id',
        'url',
        'status',
        'quiz__name',
        'quiz__description',
        'quiz__url',
        'quiz__subject',
        'quiz__topic',
        'quiz__difficulty'
    ]

    def quiz_link(self, quizAttempt):
        if not quizAttempt.quiz:
            return None

        app_label = quizAttempt.quiz._meta.app_label
        model_name = quizAttempt.quiz._meta.model_name
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[quizAttempt.quiz.id])
        return format_html('<a href="{}">{}</a>', url, quizAttempt.quiz)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'url',
        'subject',
        'difficulty'
    ]
    list_filter = [
        'subject',
        'difficulty',
        'isExamPaper',
        'isDraft',
        'enableAutoMarking'
    ]
    search_fields = [
        'id',
        'name',
        'description',
        'url',
        'subject',
        'topic',
        'difficulty'
    ]


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'url',
        'question_link',
        'question__questionType'
    ]
    list_filter = [
        'question__questionType'
    ]
    search_fields = [
        'id',
        'url',
        'answer',
        'choices',
        'trueOrFalse',
        'question__url',
        'question__content',
        'question__explanation',
        'question__questionType',
        'question__quiz__name',
        'question__quiz__description',
        'question__quiz__url',
        'question__quiz__subject',
        'question__quiz__topic',
        'question__quiz__difficulty'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question')

    def question_link(self, response):
        if not response.question:
            return None

        app_label = response.question._meta.app_label
        model_name = response.question._meta.model_name
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[response.question.id])
        return format_html('<a href="{}">{}</a>', url, response.question)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'quizAttempt_link'
    ]
    search_fields = [
        'id',
        'quizAttempt__url',
        'quizAttempt__status',
        'quizAttempt__quiz__name',
        'quizAttempt__quiz__description',
        'quizAttempt__quiz__url',
        'quizAttempt__quiz__subject',
        'quizAttempt__quiz__topic',
        'quizAttempt__quiz__difficulty'
    ]

    def quizAttempt_link(self, result):
        if not result.quizAttempt:
            return None

        app_label = result.quizAttempt._meta.app_label
        model_name = result.quizAttempt._meta.model_name
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[result.quizAttempt.id])
        return format_html('<a href="{}">{}</a>', url, result.quizAttempt)


auditlog.register(Question)
auditlog.register(Quiz)
auditlog.register(QuizAttempt)
auditlog.register(Response)
auditlog.register(Result)
