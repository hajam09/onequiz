from django.contrib.auth.decorators import login_required
from django.urls import path

from core import views
from core.api import *

app_name = "core"

urlpatterns = [
    path('', views.indexView, name='index-view'),
    path('quiz/create/', views.quizCreateView, name='quiz-create-view'),
    path('quiz/<int:quizId>/update/', views.quizUpdateView, name='quiz-update-view'),
    path('quiz/<int:quizId>/create-essay-question/', views.essayQuestionCreateView, name='essay-question-create-view'),
    path('quiz/<int:quizId>/create-multiple-choice-question/', views.multipleChoiceQuestionCreateView, name='multiple-choice-question-create-view'),
    path('quiz/<int:quizId>/create-true-or-false-question/', views.trueOrFalseQuestionCreateView, name='true-or-false-question-create-view'),
    path('quiz/<int:quizId>/question/<int:questionId>/update', views.questionUpdateView, name='question-update-view'),
    path('my-quizzes/', views.userCreatedQuizzesView, name='user-created-quizzes-view'),
    path('quiz-attempt/<int:attemptId>/', views.quizAttemptView, name='quiz-attempt-view'),
    path('quiz-attempt/<int:attemptId>/result', views.quizAttemptResultView, name='quiz-attempt-result-view'),
    path('quiz/<int:quizId>/attempts/', views.quizAttemptsForQuizView, name='quiz-attempts-for-quiz-view'),
    path('my-attempted-quizzes/', login_required(views.AttemptedQuizzesView.as_view()), name='attempted-quizzes-view'),
]

urlpatterns += [
    path(
        'api/v1/quizAttemptObjectApiEventVersion1Component/',
        QuizAttemptObjectApiEventVersion1Component.as_view(),
        name='quizAttemptObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/quizAttemptQuestionsApiEventVersion1Component/<int:id>',
        QuizAttemptQuestionsApiEventVersion1Component.as_view(),
        name='quizAttemptQuestionsApiEventVersion1Component'
    ),
    path(
        'api/v1/quizMarkingOccurrenceApiEventVersion1Component/<int:id>',
        QuizMarkingOccurrenceApiEventVersion1Component.as_view(),
        name='quizMarkingOccurrenceApiEventVersion1Component'
    ),
    path(
        'api/v1/questionResponseUpdateApiEventVersion1Component/',
        QuestionResponseUpdateApiEventVersion1Component.as_view(),
        name='questionResponseUpdateApiEventVersion1Component'
    ),
]
