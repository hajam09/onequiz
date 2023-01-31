import operator
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.generic import ListView

from onequiz.operations import generalOperations
from quiz.forms import (
    EssayQuestionCreateForm, EssayQuestionUpdateForm, MultipleChoiceQuestionCreateForm,
    MultipleChoiceQuestionUpdateForm, QuizCreateForm, TrueOrFalseQuestionCreateForm,
    TrueOrFalseQuestionUpdateForm, QuizUpdateForm
)
from quiz.models import (
    Question, Quiz, QuizAttempt, Result
)


def indexView(request):
    context = {
        'quizList': generalOperations.performComplexQuizSearch(request.GET.get('query'))
    }
    return render(request, 'quiz/quizListView.html', context)


@login_required
def createEssayQuestionView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = EssayQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            newEssayQuestion = form.save()
            quiz.questions.add(newEssayQuestion.question)
            return redirect('quiz:create-essay-question-view', quizId=quizId)
    else:
        form = EssayQuestionCreateForm()

    formTitle = 'Create Essay Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'quiz/essayQuestionTemplateView.html', context)


@login_required
def createMultipleChoiceQuestionView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = MultipleChoiceQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            newMultipleChoiceQuestion = form.save()
            quiz.questions.add(newMultipleChoiceQuestion.question)
            return redirect('quiz:create-multiple-choice-question-view', quizId=quizId)
    else:
        form = MultipleChoiceQuestionCreateForm()

    formTitle = 'Create Multiple Choice Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'quiz/multipleChoiceQuestionTemplateView.html', context)


@login_required
def createTrueOrFalseQuestionView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = TrueOrFalseQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            newTrueOrFalseQuestion = form.save()
            quiz.questions.add(newTrueOrFalseQuestion.question)
            return redirect('quiz:create-true-or-false-question-view', quizId=quizId)
    else:
        form = TrueOrFalseQuestionCreateForm()

    formTitle = 'Create True or False Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'quiz/trueOrFalseQuestionTemplateView.html', context)


@login_required
def createQuizView(request):
    if request.method == "POST":
        form = QuizCreateForm(request, request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz:create-quiz')
    else:
        form = QuizCreateForm(request)

    formTitle = 'Create Quiz'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'quiz/quizTemplateView.html', context)


@login_required
def quizDetailView(request, quizId):
    try:
        quiz = Quiz.objects.select_related('topic').get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    quizQuestions = quiz.getQuestions()

    if request.method == "POST":
        form = QuizUpdateForm(request, quiz, request.POST, request.FILES)
        if form.is_valid():
            form.update()
            return redirect('quiz:quiz-detail-view', quizId=quizId)
    else:
        form = QuizUpdateForm(request, quiz)

    formTitle = 'View or Update Quiz'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizId': quizId,
        'quizQuestions': quizQuestions,
    }
    return render(request, 'quiz/quizTemplateView.html', context)


@login_required
def questionDetailView(request, quizId, questionId):
    try:
        question = Question.objects.select_related(
            'essayQuestion', 'trueOrFalseQuestion', 'multipleChoiceQuestion').get(
            id=questionId, quizQuestions=quizId, quizQuestions__creator=request.user
        )
    except Question.DoesNotExist:
        raise Http404

    form = None
    template = None
    formTitle = None

    if hasattr(question, 'essayQuestion'):
        if request.method == "POST":
            form = EssayQuestionUpdateForm(question.essayQuestion, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('quiz:question-detail-view', quizId=quizId, questionId=questionId)
        else:
            form = EssayQuestionUpdateForm(question.essayQuestion)

        template = 'quiz/essayQuestionTemplateView.html'
        formTitle = 'View or Update Essay Question'

    elif hasattr(question, 'trueOrFalseQuestion'):
        if request.method == "POST":
            form = TrueOrFalseQuestionUpdateForm(question.trueOrFalseQuestion, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('quiz:question-detail-view', quizId=quizId, questionId=questionId)
        else:
            form = TrueOrFalseQuestionUpdateForm(question.trueOrFalseQuestion)

        template = 'quiz/trueOrFalseQuestionTemplateView.html'
        formTitle = 'View or Update True or False Question'

    elif hasattr(question, 'multipleChoiceQuestion'):
        if request.method == "POST":
            form = MultipleChoiceQuestionUpdateForm(question.multipleChoiceQuestion, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('quiz:question-detail-view', quizId=quizId, questionId=questionId)
        else:
            form = MultipleChoiceQuestionUpdateForm(question.multipleChoiceQuestion)

        template = 'quiz/multipleChoiceQuestionTemplateView.html'
        formTitle = 'View or Update Multiple Choice Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, template, context)


@login_required
def userCreatedQuizzesView(request):
    filterList = [
        reduce(
            operator.or_, [Q(**{'creator_id': request.user.id})]
        )
    ]

    context = {
        'quizList': generalOperations.performComplexQuizSearch(request.GET.get('query'), filterList)
    }
    return render(request, 'quiz/quizListView.html', context)


@login_required
def quizAttemptView(request, attemptId):
    try:
        quizAttempt = QuizAttempt.objects.select_related('user', 'quiz__creator').get(id=attemptId)
    except QuizAttempt.DoesNotExist:
        raise Http404

    if quizAttempt.hasQuizEnded() and quizAttempt.status in quizAttempt.getEditStatues():
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    if not quizAttempt.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    context = {
        'quizAttempt': quizAttempt,
        'mode': quizAttempt.getPermissionMode(request.user),
    }
    return render(request, 'quiz/quizAttemptView.html', context)


@login_required
def quizAttemptResultView(request, attemptId):
    result = Result.objects.filter(quizAttempt__id=attemptId).select_related(
        'quizAttempt__user', 'quizAttempt__quiz__creator'
    ).last()
    if result is None:
        # TODO: Raise a template that quiz attempt does not have a result or its not yet to be viewed.
        raise Http404

    if not result.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    data = [
        {'key': 'Quiz', 'value': result.quizAttempt.quiz.name},
        None,
        {'key': 'Total Questions', 'value': result.quizAttempt.quiz.questions.count()},
        {'key': 'Correct Answers', 'value': result.numberOfCorrectAnswers},
        {'key': 'Partially Correct Answers', 'value': result.numberOfPartialAnswers},
        {'key': 'Wrong Answers', 'value': result.numberOfWrongAnswers},
        {'key': 'Your Score', 'value': f'{result.score} %'},
        {'key': 'Your Time', 'value': result.getTimeSpent()},
        {'key': 'Marked By', 'value': result.quizAttempt.quiz.creator.get_full_name()},
    ]

    context = {
        'result': result,
        'data': data,
    }
    return render(request, 'quiz/quizAttemptResultView.html', context)


class AttemptedQuizzesView(ListView):
    model = QuizAttempt
    template_name = 'quiz/attemptedQuizzesView.html'
    context_object_name = 'quizAttemptList'

    def get_queryset(self):
        return QuizAttempt.objects.select_related('quiz__topic__subject').filter(user=self.request.user)


@login_required
def quizAttemptsForQuizView(request, quizId):
    quizAttemptList = QuizAttempt.objects.select_related('user').filter(quiz_id=quizId)
    context = {
        'quizAttemptList': quizAttemptList,
        'quizId': quizId,
    }
    return render(request, 'quiz/quizAttemptsForQuizView.html', context)
