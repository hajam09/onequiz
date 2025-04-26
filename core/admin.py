from auditlog.registry import auditlog
from django.contrib import admin

from core.models import (
    Question,
    QuizAttempt,
    Quiz,
    Response,
    Result
)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    pass


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    pass


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    pass


auditlog.register(Question)
auditlog.register(Quiz)
auditlog.register(QuizAttempt)
auditlog.register(Response)
auditlog.register(Result)
