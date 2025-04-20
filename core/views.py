import operator
import random
from functools import reduce

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView

from core.forms import (
    EssayQuestionCreateForm, MultipleChoiceQuestionCreateForm, TrueOrFalseQuestionCreateForm,
    EssayQuestionUpdateForm, MultipleChoiceQuestionUpdateForm, TrueOrFalseQuestionUpdateForm,
    QuizCreateForm, QuizUpdateForm, EssayQuestionResponseForm, TrueOrFalseQuestionResponseForm,
    MultipleChoiceQuestionResponseForm,
)
from core.models import Quiz, Question, QuizAttempt, Result, Response
from onequiz.operations import generalOperations
from onequiz.operations.generalOperations import QuizAttemptManualMarking, QuizAttemptAutomaticMarking


def indexView(request):
    context = {
        'subjects': Quiz.Subject.choices
    }
    return render(request, 'core/index.html', context)


def quizListView(request):
    filterList = [
        reduce(
            operator.and_, [Q(**{'isDraft': False})]
        )
    ]
    quizList = generalOperations.performComplexQuizSearch(request.GET.get('query'), filterList)

    paginator = Paginator(quizList, 10)
    page = request.GET.get('page')

    try:
        quizList = paginator.page(page)
    except PageNotAnInteger:
        quizList = paginator.page(1)
    except EmptyPage:
        quizList = paginator.page(paginator.num_pages)

    context = {
        'quizList': quizList
    }
    return render(request, 'core/quizListView.html', context)


@login_required
def quizCreateView(request):
    if request.method == 'POST':
        form = QuizCreateForm(request, request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:quiz-create-view')
    else:
        form = QuizCreateForm(request)

    formTitle = 'Create Quiz'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'core/quizTemplateView.html', context)


def quizUpdateView(request, url):
    quiz = get_object_or_404(Quiz, url=url)  # creator=request.user

    if request.method == 'POST':
        form = QuizUpdateForm(request, quiz, request.POST, request.FILES)
        if form.is_valid():
            form.update()
            return redirect('core:quiz-update-view', url=url)
    else:
        form = QuizUpdateForm(request, quiz)

    formTitle = 'View or Update Quiz' if quiz.creator_id == request.user.id else 'View Quiz'
    quizQuestions = quiz.getQuestions()

    context = {
        'form': form,
        'formTitle': formTitle,
        'quiz': quiz,
        'quizQuestions': quizQuestions,
    }
    return render(request, 'core/quizTemplateView.html', context)


@login_required
def essayQuestionCreateView(request, url):
    quiz = get_object_or_404(Quiz, url=url, creator=request.user)

    if request.method == 'POST':
        form = EssayQuestionCreateForm(quiz, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:essay-question-create-view', url=url)
    else:
        form = EssayQuestionCreateForm(quiz)

    formTitle = 'Create Essay Question'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizUrl': url,
    }
    return render(request, 'core/essayQuestionTemplateView.html', context)


@login_required
def multipleChoiceQuestionCreateView(request, url):
    quiz = get_object_or_404(Quiz, url=url, creator=request.user)

    if request.method == 'POST':
        form = MultipleChoiceQuestionCreateForm(quiz, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:multiple-choice-question-create-view', url=url)
    else:
        form = MultipleChoiceQuestionCreateForm(quiz)

    formTitle = 'Create Multiple Choice Question'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizUrl': url,
    }
    return render(request, 'core/multipleChoiceQuestionTemplateView.html', context)


@login_required
def trueOrFalseQuestionCreateView(request, url):
    quiz = get_object_or_404(Quiz, url=url, creator=request.user)

    if request.method == 'POST':
        form = TrueOrFalseQuestionCreateForm(quiz, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:true-or-false-question-create-view', url=url)
    else:
        form = TrueOrFalseQuestionCreateForm(quiz)

    formTitle = 'Create True or False Question'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizUrl': url,
    }
    return render(request, 'core/trueOrFalseQuestionTemplateView.html', context)


@login_required
def questionUpdateView(request, quizUrl, questionUrl):
    question = get_object_or_404(Question, url=questionUrl, quiz__url=quizUrl, quiz__creator=request.user)

    form = None
    template = None
    formTitle = None

    if question.questionType == Question.Type.ESSAY:
        if request.method == 'POST':
            form = EssayQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('core:question-update-view', quizUrl=quizUrl, questionUrl=questionUrl)
        else:
            form = EssayQuestionUpdateForm(question)

        template = 'core/essayQuestionTemplateView.html'
        formTitle = 'View or Update Essay Question'

    elif question.questionType == Question.Type.TRUE_OR_FALSE:
        if request.method == 'POST':
            form = TrueOrFalseQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('core:question-update-view', quizUrl=quizUrl, questionUrl=questionUrl)
        else:
            form = TrueOrFalseQuestionUpdateForm(question)

        template = 'core/trueOrFalseQuestionTemplateView.html'
        formTitle = 'View or Update True or False Question'

    elif question.questionType == Question.Type.MULTIPLE_CHOICE:
        if request.method == 'POST':
            form = MultipleChoiceQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('core:question-update-view', quizUrl=quizUrl, questionUrl=questionUrl)
        else:
            form = MultipleChoiceQuestionUpdateForm(question)

        template = 'core/multipleChoiceQuestionTemplateView.html'
        formTitle = 'View or Update Multiple Choice Question'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizUrl': quizUrl,
    }
    return render(request, template, context)


@login_required
def userCreatedQuizzesView(request):
    filterList = [
        reduce(
            operator.or_, [Q(**{'creator_id': request.user.id})]
        )
    ]

    quizList = generalOperations.performComplexQuizSearch(request.GET.get('query'), filterList)

    paginator = Paginator(quizList, 10)
    page = request.GET.get('page')

    try:
        quizList = paginator.page(page)
    except PageNotAnInteger:
        quizList = paginator.page(1)
    except EmptyPage:
        quizList = paginator.page(paginator.num_pages)

    context = {
        'quizList': quizList
    }
    return render(request, 'core/quizListView.html', context)


@login_required
def quizAttemptViewVersion1(request, url):
    quizAttempt = get_object_or_404(QuizAttempt.objects.select_related('user'), url=url)

    if quizAttempt.hasQuizEnded() and quizAttempt.status in quizAttempt.getEditStatues():
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    if not quizAttempt.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    if quizAttempt.getPermissionMode(request.user) == QuizAttempt.Mode.MARK:
        # Quiz creator wants to mark this quiz. Temporarily redirect to quizAttemptSubmissionPreview and mark there.
        return redirect('core:quiz-attempt-submission-preview', url=url)

    responseUrls = cache.get(f'quiz-attempt-v1-{url}')
    if responseUrls is None:
        responseUrls = list(quizAttempt.responses.values_list('url', flat=True))
        if quizAttempt.quiz.inRandomOrder:
            random.shuffle(responseUrls)
        cache.set(
            f'quiz-attempt-v1-{quizAttempt.url}',
            responseUrls,
            quizAttempt.quiz.quizDuration * 60 + 30
        )

    responseUrl = request.GET.get('r')
    if responseUrl not in responseUrls:
        return redirect(f'/v1/quiz-attempt/{url}/?r={responseUrls[0]}')

    responseObject = quizAttempt.responses.filter(url=responseUrl).first()

    if request.method == 'POST' and 'submitResponse' in request.POST:
        if not quizAttempt.hasQuizEnded():
            if responseObject.question.questionType == Question.Type.ESSAY:
                responseObject.answer = request.POST.get('answer')
            elif responseObject.question.questionType == Question.Type.TRUE_OR_FALSE:
                responseObject.trueOrFalse = request.POST.get('trueOrFalse')
            elif responseObject.question.questionType == Question.Type.MULTIPLE_CHOICE:
                optionsKey = next((key for key in request.POST if key.startswith('option')), None)
                checkedOptionsIds = set(request.POST.getlist(optionsKey))
                for choice in responseObject.choices.get('choices'):
                    choice['isChecked'] = choice['id'] in checkedOptionsIds
            responseObject.save()

        responseIndex = responseUrls.index(responseUrl)
        if request.POST.get('submitResponse') == 'next':
            isLastElement = responseIndex == len(responseUrls) - 1
            if isLastElement:
                return redirect('core:quiz-attempt-submission-preview', url=url)
            return redirect(f'/v1/quiz-attempt/{url}/?r={responseUrls[responseIndex + 1]}')
        elif request.POST.get('submitResponse') == 'previous' and responseIndex != 0:
            return redirect(f'/v1/quiz-attempt/{url}/?r={responseUrls[responseIndex - 1]}')
        else:
            raise Exception('Invalid POST action')

    hasQuizEnded = not quizAttempt.hasQuizEnded()

    if responseObject.question.questionType == Question.Type.ESSAY:
        form = EssayQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    elif responseObject.question.questionType == Question.Type.TRUE_OR_FALSE:
        form = TrueOrFalseQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    elif responseObject.question.questionType == Question.Type.MULTIPLE_CHOICE:
        form = MultipleChoiceQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    else:
        raise Exception('Invalid question type')

    context = {
        'quizAttempt': quizAttempt,
        'responseUrls': responseUrls,
        'form': form,
        'has_previous': responseUrls.index(responseUrl) != 0,
        'progress': {
            'current': responseUrls.index(responseUrl) + 1,
            'total': len(responseUrls),
            'percentage': round(((responseUrls.index(responseUrl) + 1) / len(responseUrls)) * 100, 0)
        }
    }
    return render(request, 'core/quizAttemptViewVersion1.html', context)


@login_required
def quizAttemptSubmissionPreview(request, url):
    quizAttempt = get_object_or_404(QuizAttempt.objects.select_related('quiz', 'user'), url=url)

    if quizAttempt.hasQuizEnded() and quizAttempt.status in quizAttempt.getEditStatues():
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    if not quizAttempt.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    isQuizParticipant = quizAttempt.user == request.user
    # - > User views all their response.
    # - > User submits their quiz attempt.
    if isQuizParticipant and request.method == 'POST' and 'submitQuiz' in request.POST:
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        cache.delete(f'quiz-attempt-v1-{url}')

        if quizAttempt.quiz.enableAutoMarking:
            quizAttemptAutomaticMarking = QuizAttemptAutomaticMarking(
                quizAttempt, quizAttempt.responses.select_related('question').all()
            )
            marked = quizAttemptAutomaticMarking.mark()
            if marked:
                quizAttempt.status = QuizAttempt.Status.MARKED
                messages.success(
                    request,
                    'This quiz attempt has been auto marked successfully.'
                )
            else:
                messages.success(
                    request,
                    'This quiz attempt will be marked manually by the author.'
                )
        else:
            messages.success(
                request,
                'Your quiz attempt will be marked manually by the author.'
            )

        quizAttempt.save(update_fields=['status'])
        return redirect('core:quiz-attempt-submission-preview', url=url)

    responseForms = []
    responseBorders = []
    responses = quizAttempt.responses.select_related('question').all()
    for response in responses:
        isQuizCreator = quizAttempt.quiz.creator == request.user
        confirmMark = request.method == 'POST' and 'submitQuiz' in request.POST and isQuizCreator

        if response.question.questionType == Question.Type.ESSAY:
            if confirmMark:
                response.mark = request.POST.get(f'awarded-mark-for-essay-{response.id}')
            form = EssayQuestionResponseForm(response=response, allowEdit=False, validateMark=confirmMark)

        elif response.question.questionType == Question.Type.TRUE_OR_FALSE:
            if confirmMark:
                response.mark = request.POST.get(f'awarded-mark-for-true-or-false-{response.id}')
            form = TrueOrFalseQuestionResponseForm(response=response, allowEdit=False, validateMark=confirmMark)

        elif response.question.questionType == Question.Type.MULTIPLE_CHOICE:
            if confirmMark:
                response.mark = request.POST.get(f'awarded-mark-for-mcq-{response.id}')
            form = MultipleChoiceQuestionResponseForm(response=response, allowEdit=False, validateMark=confirmMark)

        else:
            raise Exception(f'Unknown question type: {response.question.questionType} for response ID: {response.id}')

        responseForms.append(form)
        if confirmMark:
            responseBorders.append(form.data.get('markResponseAlert'))

    if 'border border-danger' in responseBorders:
        messages.error(
            request,
            'Please ensure that you have assigned correct marks to all responses.'
        )
    if responseBorders and all(element == 'border border-success' for element in responseBorders):
        Response.objects.bulk_update(responses, ['mark'])
        quizAttempt.status = QuizAttempt.Status.MARKED
        quizAttempt.save(update_fields=['status'])

        quizAttemptManualMarking = QuizAttemptManualMarking(quizAttempt, responses)
        quizAttemptManualMarking.mark()

        messages.success(
            request,
            'You have marked this quiz attempt successfully.'
        )
        return redirect('core:quiz-attempt-submission-preview', url=url)

    context = {
        'quizAttempt': quizAttempt,
        'forms': responseForms,
    }
    return render(request, 'core/quizAttemptReviewView.html', context)


def quizAttemptResultView(request, url):
    result = Result.objects.filter(
        Q(quizAttempt__url=url, quizAttempt__user_id=request.user.id) |
        Q(quizAttempt__url=url, quizAttempt__quiz__creator_id=request.user.id)
    ).select_related('quizAttempt__quiz__creator').last()

    if result is None:
        raise Http404

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
    return render(request, 'core/quizAttemptResultView.html', context)


def quizAttemptsForQuizView(request, url):
    quizAttemptList = QuizAttempt.objects.select_related('user').filter(quiz__url=url)
    context = {
        'quizAttemptList': quizAttemptList,
        'url': url,
    }
    return render(request, 'core/quizAttemptsForQuizView.html', context)


class AttemptedQuizzesView(ListView):
    model = QuizAttempt
    template_name = 'core/attemptedQuizzesView.html'
    context_object_name = 'quizAttemptList'

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)
