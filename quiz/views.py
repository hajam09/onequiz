import operator
from functools import reduce

from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from quiz.forms import (
    EssayQuestionCreateForm, EssayQuestionUpdateForm, MultipleChoiceQuestionCreateForm,
    MultipleChoiceQuestionUpdateForm, QuizCreateForm, TrueOrFalseQuestionCreateForm,
    TrueOrFalseQuestionUpdateForm, QuizUpdateForm
)
from quiz.models import (
    EssayQuestion, MultipleChoiceQuestion, Question, Quiz, TrueOrFalseQuestion, QuizAttempt, Result
)


def indexView(request):
    return render(request, 'quiz/indexView.html')


def createEssayQuestionView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = EssayQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            newEssayQuestion = form.save()
            quiz.questions.add(newEssayQuestion)
            return redirect('quiz:create-essay-question-view', quizId=quizId)
    else:
        form = EssayQuestionCreateForm()

    formTitle = 'Create Essay Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'quiz/essayQuestionTemplateView.html', context)


def createMultipleChoiceQuestionView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = MultipleChoiceQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            newMultipleChoiceQuestion = form.save()
            quiz.questions.add(newMultipleChoiceQuestion)
            return redirect('quiz:create-multiple-choice-question-view', quizId=quizId)
    else:
        form = MultipleChoiceQuestionCreateForm()

    formTitle = 'Create Multiple Choice Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'quiz/multipleChoiceQuestionTemplateView.html', context)


def createTrueOrFalseQuestionView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = TrueOrFalseQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            newTrueOrFalseQuestion = form.save()
            quiz.questions.add(newTrueOrFalseQuestion)
            return redirect('quiz:create-true-or-false-question-view', quizId=quizId)
    else:
        form = TrueOrFalseQuestionCreateForm()

    formTitle = 'Create True or False Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'quiz/trueOrFalseQuestionTemplateView.html', context)


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
    return render(request, 'quiz/createQuizView.html', context)


def quizDetailView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
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

    template = 'quiz/essayQuestionTemplateView.html'
    formTitle = 'View or Update Quiz'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizId': quizId,
        'quizQuestions': quizQuestions,
    }
    return render(request, 'quiz/quizDetailView.html', context)


def questionDetailView(request, quizId, questionId):
    try:
        question = Question.objects.get_subclass(id=questionId, quizQuestions=quizId)
    except Question.DoesNotExist:
        raise Http404

    form = None
    template = None
    formTitle = None

    if isinstance(question, EssayQuestion):
        if request.method == "POST":
            form = EssayQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('quiz:question-detail-view', quizId=quizId, questionId=questionId)
        else:
            form = EssayQuestionUpdateForm(question)

        template = 'quiz/essayQuestionTemplateView.html'
        formTitle = 'View or Update Essay Question'

    elif isinstance(question, TrueOrFalseQuestion):
        if request.method == "POST":
            form = TrueOrFalseQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('quiz:question-detail-view', quizId=quizId, questionId=questionId)
        else:
            form = TrueOrFalseQuestionUpdateForm(question)

        template = 'quiz/trueOrFalseQuestionTemplateView.html'
        formTitle = 'View or Update True or False Question'

    elif isinstance(question, MultipleChoiceQuestion):
        if request.method == "POST":
            form = MultipleChoiceQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('quiz:question-detail-view', quizId=quizId, questionId=questionId)
        else:
            form = MultipleChoiceQuestionUpdateForm(question)

        template = 'quiz/multipleChoiceQuestionTemplateView.html'
        formTitle = 'View or Update Multiple Choice Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, template, context)


def userCreatedQuizzesView(request):
    query = request.GET.get('query')
    qFilterSet = []
    attributesToSearch = [
        'name', 'description', 'url',
        'topic__name', 'topic__description',
        'topic__subject__name', 'topic__subject__description'
    ]

    if query and query.strip():
        qFilterSet.append(
            reduce(
                operator.or_, [Q(**{f'{v}__icontains': query}) for v in attributesToSearch]
            )
        )

    qFilterSet.append(
        reduce(
            operator.or_, [Q(**{'creator_id': request.user.id})]
        )
    )

    quizList = Quiz.objects.filter(reduce(operator.and_, qFilterSet)).select_related('topic__subject').distinct()
    context = {
        'quizList': quizList
    }
    return render(request, 'quiz/userCreatedQuizzesView.html', context)


def quizAttemptView(request, attemptId):
    try:
        quizAttempt = QuizAttempt.objects.select_related('user', 'quiz__creator').get(id=attemptId)
    except QuizAttempt.DoesNotExist:
        raise Http404

    if quizAttempt.user != request.user or quizAttempt.quiz.creator != request.user:
        # return 401 page.
        return HttpResponse('Unauthorized', status=401)

    quizNotSubmittedStatues = [QuizAttempt.Status.NOT_ATTEMPTED, QuizAttempt.Status.IN_PROGRESS]
    if timezone.now() > quizAttempt.getQuizEndTime(False) and quizAttempt.status in quizNotSubmittedStatues:
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    context = {
        'quizAttempt': quizAttempt,
        'mode': quizAttempt.getPermissionMode(request.user),
    }
    return render(request, 'quiz/quizAttemptView.html', context)


def quizAttemptResultView(request, attemptId):
    result = Result.objects.select_related('quizAttempt__quiz').filter(quizAttempt__id=attemptId).order_by('-id')
    if result.count() == 0:
        raise Http404
    result = result[0]

    data = [
        {'key': 'Quiz', 'value': result.quizAttempt.quiz.name},
        None,
        {'key': 'Total Questions', 'value': result.quizAttempt.quiz.questions.count},
        {'key': 'Correct Questions', 'value': result.numberOfCorrectAnswers},
        {'key': 'Partial Questions', 'value': result.numberOfPartialAnswers},
        {'key': 'Wrong Questions', 'value': result.numberOfWrongAnswers},
        {'key': 'Your Score', 'value': f'{result.score} %'},
        {'key': 'Your Time', 'value': result.getTimeSpent()},
    ]

    context = {
        'result': result,
        'data': data,
    }
    return render(request, 'quiz/quizAttemptResultView.html', context)


def attemptedQuizzesView(request):
    quizAttemptList = QuizAttempt.objects.filter(user=request.user)
    context = {
        'quizAttemptList': quizAttemptList
    }
    return render(request, 'quiz/attemptedQuizzesView.html', context)


def quizAttemptsForQuizView(request, quizId):
    quizAttemptList = QuizAttempt.objects.filter(quiz_id=quizId)
    context = {
        'quizAttemptList': quizAttemptList
    }
    return render(request, 'quiz/quizAttemptsForQuizView.html', context)
