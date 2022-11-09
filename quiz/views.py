from django.http import Http404
from django.shortcuts import render, redirect

from quiz.forms import QuizCreationForm, TrueOrFalseQuestionForm, EssayQuestionForm
from quiz.models import Quiz


def createEssayQuestionView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = EssayQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            newEssayQuestion = form.save()
            quiz.questions.add(newEssayQuestion)
            return redirect('quiz:create-essay-question-view', quizId=quizId)
    else:
        form = EssayQuestionForm()

    context = {
        'form': form,
    }
    return render(request, 'quiz/createEssayQuestionView.html', context)


def createMultipleChoiceQuestionView(request, quizId):
    pass


def createTrueOfFalseQuestionView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = TrueOrFalseQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            newTrueOfFalseQuestion = form.save()
            quiz.questions.add(newTrueOfFalseQuestion)
            return redirect('quiz:create-true-or-false-question-view', quizId=quizId)
    else:
        form = TrueOrFalseQuestionForm()

    context = {
        'form': form,
    }
    return render(request, 'quiz/createTrueOfFalseQuestionView.html', context)


def createQuizView(request):
    if request.method == "POST":
        form = QuizCreationForm(request, request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz:create-quiz')
    else:
        form = QuizCreationForm(request)

    context = {
        'form': form,
    }
    return render(request, 'quiz/createQuizView.html', context)


def quizDetailView(request):
    pass


def userCreatedQuizzes(request):
    pass


def userAttemptedQuizzes(request):
    pass
