from django.urls import path

from quiz import views
from quiz.api import *

app_name = "quiz"

urlpatterns = [
    path('create-quiz/', views.createQuizView, name='create-quiz'),
]

urlpatterns += [
    path(
        'api/v1/topicObjectApiEventVersion1Component/',
        TopicObjectApiEventVersion1Component.as_view(),
        name='topicObjectApiEventVersion1Component'
    ),
]
