from django.contrib.auth.decorators import login_required
from django.urls import path

from core.api import (
    QuizAttemptCommenceApiVersion1
)
from core.views import (
    indexView,
    quizListView,
    quizCreateView,
    quizUpdateView,
    essayQuestionCreateView,
    multipleChoiceQuestionCreateView,
    trueOrFalseQuestionCreateView,
    questionUpdateView,
    userCreatedQuizzesView,
    quizAttemptViewVersion1,
    quizAttemptSubmissionPreview,
    quizAttemptResultView,
    quizAttemptsForQuizView,
    AttemptedQuizzesView
)

app_name = 'core'

urlpatterns = [
    path('', indexView, name='index-view'),
    path('quiz-list/', quizListView, name='quiz-list-view'),
    path('quiz/create/', quizCreateView, name='quiz-create-view'),
    path('quiz/<slug:url>/update/', quizUpdateView, name='quiz-update-view'),
    path('quiz/<slug:url>/create-essay-question/', essayQuestionCreateView, name='essay-question-create-view'),
    path('quiz/<slug:url>/create-multiple-choice-question/', multipleChoiceQuestionCreateView, name='multiple-choice-question-create-view'),
    path('quiz/<slug:url>/create-true-or-false-question/', trueOrFalseQuestionCreateView, name='true-or-false-question-create-view'),
    path('quiz/<slug:quizUrl>/question/<slug:questionUrl>/update/', questionUpdateView, name='question-update-view'),
    path('my-quizzes/', userCreatedQuizzesView, name='user-created-quizzes-view'),
    path('v1/quiz-attempt/<slug:url>/', quizAttemptViewVersion1, name='quiz-attempt-view-v1'),
    path('quiz-attempt/<slug:url>/preview/', quizAttemptSubmissionPreview, name='quiz-attempt-submission-preview'),
    path('quiz-attempt/<slug:url>/result/', quizAttemptResultView, name='quiz-attempt-result-view'),
    path('quiz/<slug:url>/attempts/', quizAttemptsForQuizView, name='quiz-attempts-for-quiz-view'),
    path('my-attempted-quizzes/', login_required(AttemptedQuizzesView.as_view()), name='attempted-quizzes-view'),
]

urlpatterns += [
    path(
        'api/v1/quizAttemptCommenceApiVersion1/',
        QuizAttemptCommenceApiVersion1.as_view(),
        name='quizAttemptCommenceApiVersion1'
    ),
]
