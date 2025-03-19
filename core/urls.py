from django.contrib.auth.decorators import login_required
from django.urls import path

from core.api import (
    QuestionResponseUpdateApiEventVersion1Component,
    QuizAttemptObjectApiEventVersion1Component,
    QuizAttemptObjectApiEventVersion2Component,
    QuizAttemptObjectApiEventVersion3Component,
    QuizAttemptQuestionsApiEventVersion1Component,
    QuizMarkingOccurrenceApiEventVersion1Component
)
from core.views import (
    indexView,
    quizListView,
    quizCreateView,
    quizUpdateView,
    essayQuestionCreateView,
    multipleChoiceQuestionCreateView,
    trueOrFalseQuestionCreateView,
    bulkQuestionCreateView,
    questionUpdateView,
    userCreatedQuizzesView,
    quizAttemptViewVersion1,
    quizAttemptViewVersion2,
    quizAttemptViewVersion3,
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
    path('quiz/<slug:url>/create-bulk-questions/', bulkQuestionCreateView, name='bulk-question-create-view'),
    path('quiz/<slug:quizUrl>/question/<slug:questionUrl>/update/', questionUpdateView, name='question-update-view'),
    path('my-quizzes/', userCreatedQuizzesView, name='user-created-quizzes-view'),
    path('v1/quiz-attempt/<slug:url>/', quizAttemptViewVersion1, name='quiz-attempt-view-v1'),
    path('v2/quiz-attempt/<slug:url>/', quizAttemptViewVersion2, name='quiz-attempt-view-v2'),
    path('v3/quiz-attempt/<slug:url>/', quizAttemptViewVersion3, name='quiz-attempt-view-v3'),
    path('v2/quiz-attempt/<slug:url>/preview/', quizAttemptSubmissionPreview, name='quiz-attempt-submission-preview'),
    path('quiz-attempt/<slug:url>/result/', quizAttemptResultView, name='quiz-attempt-result-view'),
    path('quiz/<slug:url>/attempts/', quizAttemptsForQuizView, name='quiz-attempts-for-quiz-view'),
    path('my-attempted-quizzes/', login_required(AttemptedQuizzesView.as_view()), name='attempted-quizzes-view'),
]

urlpatterns += [
    path(
        'api/v1/questionResponseUpdateApiEventVersion1Component/',
        QuestionResponseUpdateApiEventVersion1Component.as_view(),
        name='questionResponseUpdateApiEventVersion1Component'
    ),
    path(
        'api/v1/quizAttemptObjectApiEventVersion1Component/',
        QuizAttemptObjectApiEventVersion1Component.as_view(),
        name='quizAttemptObjectApiEventVersion1Component'
    ),
    path(
        'api/v2/quizAttemptObjectApiEventVersion2Component/',
        QuizAttemptObjectApiEventVersion2Component.as_view(),
        name='quizAttemptObjectApiEventVersion2Component'
    ),
    path(
        'api/v3/quizAttemptObjectApiEventVersion3Component/',
        QuizAttemptObjectApiEventVersion3Component.as_view(),
        name='quizAttemptObjectApiEventVersion3Component'
    ),
    path(
        'api/v1/quizAttemptQuestionsApiEventVersion1Component/<int:id>/',
        QuizAttemptQuestionsApiEventVersion1Component.as_view(),
        name='quizAttemptQuestionsApiEventVersion1Component'
    ),
    path(
        'api/v1/quizMarkingOccurrenceApiEventVersion1Component/<int:id>/',
        QuizMarkingOccurrenceApiEventVersion1Component.as_view(),
        name='quizMarkingOccurrenceApiEventVersion1Component'
    )
]
