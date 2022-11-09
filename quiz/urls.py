from django.urls import path

from quiz import views
from quiz.api import *

app_name = "quiz"

urlpatterns = [
    path('create-quiz/', views.createQuizView, name='create-quiz'),
    path('<int:quizId>/create-true-or-false-question/', views.createTrueOfFalseQuestionView, name='create-true-or-false-question-view'),
    path('<int:quizId>/create-essay-question/', views.createEssayQuestionView, name='create-essay-question-view'),
]

urlpatterns += [
    path(
        'api/v1/topicObjectApiEventVersion1Component/',
        TopicObjectApiEventVersion1Component.as_view(),
        name='topicObjectApiEventVersion1Component'
    ),
]
