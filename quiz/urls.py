from django.contrib.auth.decorators import login_required
from django.urls import path

from quiz import views
from quiz.api import *

app_name = "quiz"

urlpatterns = [
    path('', views.indexView, name='index-view'),
    path('quiz/create/', views.createQuizView, name='create-quiz'),
    path('quiz/<int:quizId>/create-true-or-false-question/', views.createTrueOrFalseQuestionView, name='create-true-or-false-question-view'),
    path('quiz/<int:quizId>/create-essay-question/', views.createEssayQuestionView, name='create-essay-question-view'),
    path('quiz/<int:quizId>/create-multiple-choice-question/', views.createMultipleChoiceQuestionView, name='create-multiple-choice-question-view'),
    path('quiz/<int:quizId>/detail/', views.quizDetailView, name='quiz-detail-view'),
    path('quiz/<int:quizId>/attempts/', views.quizAttemptsForQuizView, name='quiz-attempts-for-quiz-view'),
    path('quiz/<int:quizId>/question/<int:questionId>/detail', views.questionDetailView, name='question-detail-view'),
    path('my-quizzes/', views.userCreatedQuizzesView, name='user-created-quizzes-view'),
    path('quiz-attempt/<int:attemptId>/', views.quizAttemptView, name='quiz-attempt-view'),
    path('quiz-attempt/<int:attemptId>/result', views.quizAttemptResultView, name='quiz-attempt-result-view'),
    path('my-attempted-quizzes/', login_required(views.AttemptedQuizzesView.as_view()), name='attempted-quizzes-view'),
]

urlpatterns += [
    path(
        'api/v1/topicObjectApiEventVersion1Component/',
        TopicObjectApiEventVersion1Component.as_view(),
        name='topicObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/quizAttemptObjectApiEventVersion1Component/',
        QuizAttemptObjectApiEventVersion1Component.as_view(),
        name='quizAttemptObjectApiEventVersion1Component'
    ),
    path(
        'api/v1/questionResponseUpdateApiEventVersion1Component/',
        QuestionResponseUpdateApiEventVersion1Component.as_view(),
        name='questionResponseUpdateApiEventVersion1Component'
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
]
