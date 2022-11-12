from django.http import Http404
from django.shortcuts import render, redirect

from quiz.forms import (
    QuizCreationCreateForm, TrueOrFalseQuestionCreateForm, EssayQuestionCreateForm,
    MultipleChoiceQuestionCreateForm, EssayQuestionUpdateForm, MultipleChoiceQuestionUpdateForm,
    TrueOrFalseQuestionUpdateForm
)
from quiz.models import (
    Quiz, Question, EssayQuestion, TrueOrFalseQuestion, MultipleChoiceQuestion
)


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
    # TODO: Refactor view, and form like question objects
    if request.method == "POST":
        form = QuizCreationCreateForm(request, request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz:create-quiz')
    else:
        form = QuizCreationCreateForm(request)

    context = {
        'form': form,
    }
    return render(request, 'quiz/createQuizView.html', context)


def quizDetailView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    quizQuestionList = quiz.getQuestions()

    context = {
        'quizId': quizId,
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


def userCreatedQuizzes(request):
    pass


def userAttemptedQuizzes(request):
    pass
