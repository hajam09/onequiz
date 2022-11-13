from django.urls import path

from quiz import views
from quiz.api import *

app_name = "quiz"

urlpatterns = [
    path('create/', views.createQuizView, name='create-quiz'),
    path('<int:quizId>/create-true-or-false-question/', views.createTrueOrFalseQuestionView, name='create-true-or-false-question-view'),
    path('<int:quizId>/create-essay-question/', views.createEssayQuestionView, name='create-essay-question-view'),
    path('<int:quizId>/create-multiple-choice-question/', views.createMultipleChoiceQuestionView, name='create-multiple-choice-question-view'),
    path('<int:quizId>/detail/', views.quizDetailView, name='quiz-detail-view'),
    path('<int:quizId>/question/<int:questionId>/detail', views.questionDetailView, name='question-detail-view'),
]

urlpatterns += [
    path(
        'api/v1/topicObjectApiEventVersion1Component/',
        TopicObjectApiEventVersion1Component.as_view(),
        name='topicObjectApiEventVersion1Component'
    ),
]
