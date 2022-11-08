from django.shortcuts import render

from quiz.forms import QuizCreationForm


def createEssayQuestionView(request, quizId):
    pass


def createMultipleChoiceQuestionView(request, quizId):
    pass


def createTrueOfFalseQuestionView(request, quizId):
    pass


def createQuizView(request):
    if request.method == "POST":
        form = QuizCreationForm(request, request.POST)
        if form.is_valid():
            pass
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
