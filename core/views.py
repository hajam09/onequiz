import operator
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import OuterRef, Subquery, Value
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from core.forms import (
    EssayQuestionCreateForm, MultipleChoiceQuestionCreateForm, TrueOrFalseQuestionCreateForm,
    EssayQuestionUpdateForm, MultipleChoiceQuestionUpdateForm, TrueOrFalseQuestionUpdateForm,
    QuizCreateForm, QuizUpdateForm, EssayQuestionResponseForm, TrueOrFalseQuestionResponseForm,
    MultipleChoiceQuestionResponseForm,
)
from core.models import Quiz, Question, QuizAttempt, Result, Subject, Response
from onequiz.operations import generalOperations


def indexView(request):
    context = {
        'subjects': Subject.objects.all()
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


def quizUpdateView(request, quizId):
    try:
        quiz = Quiz.objects.select_related('subject').get(id=quizId)  # creator=request.user
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = QuizUpdateForm(request, quiz, request.POST, request.FILES)
        if form.is_valid():
            form.update()
            return redirect('core:quiz-update-view', quizId=quizId)
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
def essayQuestionCreateView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = EssayQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save()
            quiz.questions.add(question)
            return redirect('core:essay-question-create-view', quizId=quizId)
    else:
        form = EssayQuestionCreateForm()

    formTitle = 'Create Essay Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'core/essayQuestionTemplateView.html', context)


@login_required
def multipleChoiceQuestionCreateView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = MultipleChoiceQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save()
            quiz.questions.add(question)
            return redirect('core:multiple-choice-question-create-view', quizId=quizId)
    else:
        form = MultipleChoiceQuestionCreateForm()

    formTitle = 'Create Multiple Choice Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'core/multipleChoiceQuestionTemplateView.html', context)


@login_required
def trueOrFalseQuestionCreateView(request, quizId):
    try:
        quiz = Quiz.objects.get(id=quizId, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = TrueOrFalseQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save()
            quiz.questions.add(question)
            return redirect('core:true-or-false-question-create-view', quizId=quizId)
    else:
        form = TrueOrFalseQuestionCreateForm()

    formTitle = 'Create True or False Question'

    context = {
        'form': form,
        'formTitle': formTitle,
    }
    return render(request, 'core/trueOrFalseQuestionTemplateView.html', context)


@login_required
def questionUpdateView(request, quizId, questionId):
    try:
        question = Question.objects.get(
            id=questionId, quizQuestions=quizId, quizQuestions__creator=request.user
        )
    except Question.DoesNotExist:
        raise Http404

    form = None
    template = None
    formTitle = None

    if question.questionType == Question.Type.ESSAY:
        if request.method == 'POST':
            form = EssayQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('core:question-update-view', quizId=quizId, questionId=questionId)
        else:
            form = EssayQuestionUpdateForm(question)

        template = 'core/essayQuestionTemplateView.html'
        formTitle = 'View or Update Essay Question'

    elif question.questionType == Question.Type.TRUE_OR_FALSE:
        if request.method == 'POST':
            form = TrueOrFalseQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('core:question-update-view', quizId=quizId, questionId=questionId)
        else:
            form = TrueOrFalseQuestionUpdateForm(question)

        template = 'core/trueOrFalseQuestionTemplateView.html'
        formTitle = 'View or Update True or False Question'

    elif question.questionType == Question.Type.MULTIPLE_CHOICE:
        if request.method == 'POST':
            form = MultipleChoiceQuestionUpdateForm(question, request.POST, request.FILES)
            if form.is_valid():
                form.update()
                return redirect('core:question-update-view', quizId=quizId, questionId=questionId)
        else:
            form = MultipleChoiceQuestionUpdateForm(question)

        template = 'core/multipleChoiceQuestionTemplateView.html'
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
def quizAttemptViewVersion1(request, attemptId):
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
    return render(request, 'core/quizAttemptViewVersion1.html', context)


@login_required
def quizAttemptViewVersion2(request, attemptId):
    quizAttempt = get_object_or_404(QuizAttempt.objects.select_related('user'), id=attemptId)

    if quizAttempt.hasQuizEnded() and quizAttempt.status in quizAttempt.getEditStatues():
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    if not quizAttempt.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    ref = request.GET.get('ref', 'next')
    questionIndex = request.GET.get('q', 1)

    questions = Question.objects.filter(quizQuestions__id=quizAttempt.quiz_id)
    paginator = Paginator(questions, 1)

    if request.method == 'POST' and quizAttempt.status != QuizAttempt.Status.SUBMITTED:
        # When there is a POST request, it can mean the user wants to view the next question or the previous question.
        # Determine the index shift based on the navigation direction
        indexShift = -1 if ref == 'next' else 1
        respondedQuestionIndex = int(questionIndex) + indexShift
        respondedQuestionObject = paginator.page(respondedQuestionIndex).object_list[0]
        responseObject = Response.objects.get(quizAttemptResponses__in=[quizAttempt], question=respondedQuestionObject)

        if respondedQuestionObject.questionType == Question.Type.ESSAY:
            responseObject.answer = request.POST.get('answer')
        elif respondedQuestionObject.questionType == Question.Type.TRUE_OR_FALSE:
            responseObject.trueSelected = eval(str(request.POST.get('trueOrFalse')))
        elif respondedQuestionObject.questionType == Question.Type.MULTIPLE_CHOICE:
            for choice in responseObject.choices.get('choices'):
                choice['isChecked'] = choice['id'] in request.POST.getlist('options')

        responseObject.save()

    try:
        questionPaginator = paginator.page(questionIndex)
    except PageNotAnInteger:
        questionPaginator = paginator.page(1)
    except EmptyPage:
        if int(questionIndex) > paginator.num_pages:
            return redirect('core:quiz-attempt-submission-preview', attemptId=attemptId)
        questionPaginator = paginator.page(paginator.num_pages)

    currentQuestion = questionPaginator.object_list[0]
    responseObject, created = Response.objects.get_or_create(
        quizAttemptResponses__in=[quizAttempt], question=currentQuestion
    )
    quizAttempt.responses.add(responseObject.id)

    if currentQuestion.questionType == Question.Type.ESSAY:
        form = EssayQuestionResponseForm(response=responseObject, allowEdit=not quizAttempt.hasQuizEnded())
    elif currentQuestion.questionType == Question.Type.TRUE_OR_FALSE:
        form = TrueOrFalseQuestionResponseForm(response=responseObject, allowEdit=not quizAttempt.hasQuizEnded())
    elif currentQuestion.questionType == Question.Type.MULTIPLE_CHOICE:
        form = MultipleChoiceQuestionResponseForm(response=responseObject, allowEdit=not quizAttempt.hasQuizEnded())
    else:
        raise Exception('Invalid question type')

    numberOfQuestions = questionPaginator.paginator.page_range.stop - questionPaginator.paginator.page_range.start
    context = {
        'quizAttempt': quizAttempt,
        'questionPaginator': questionPaginator,
        'form': form,
        'progress': round((questionPaginator.number / numberOfQuestions) * 100, 0)
    }
    return render(request, 'core/quizAttemptViewVersion2.html', context)


@login_required
def quizAttemptSubmissionPreview(request, attemptId):
    quizAttempt = get_object_or_404(QuizAttempt.objects.select_related('user'), id=attemptId)

    if quizAttempt.hasQuizEnded() and quizAttempt.status in quizAttempt.getEditStatues():
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    if not quizAttempt.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    # Ensure all responses exist
    questions = Question.objects.filter(quizQuestions__id=quizAttempt.quiz_id)
    responsesSubquery = Response.objects.filter(
        quizAttemptResponses=quizAttempt, question_id=OuterRef('pk')
    ).values('id')[:1]
    questionsWithResponses = questions.annotate(response_id=Coalesce(Subquery(responsesSubquery), Value(None)))

    bulkResponses = []
    mcqResponses = []
    for question in questionsWithResponses.values('id', 'questionType', 'response_id'):
        if question.get('response_id') is not None:
            continue

        if question.get('questionType') == Question.Type.MULTIPLE_CHOICE:
            mcqResponses.append(Response.objects.create(question_id=question.get('id')))
        else:
            bulkResponses.append(Response(question_id=question.get('id')))

    bulkResponseCreate = Response.objects.bulk_create(bulkResponses)
    quizAttempt.responses.add(*bulkResponseCreate)
    quizAttempt.responses.add(*mcqResponses)

    responses = Response.objects.filter(
        quizAttemptResponses__in=[quizAttempt]
    ).select_related('question').order_by('question__id')
    responseForms = []
    for r in responses:
        if r.question.questionType == Question.Type.ESSAY:
            responseForms.append(EssayQuestionResponseForm(response=r, allowEdit=False))
        elif r.question.questionType == Question.Type.TRUE_OR_FALSE:
            responseForms.append(TrueOrFalseQuestionResponseForm(response=r, allowEdit=False))
        elif r.question.questionType == Question.Type.MULTIPLE_CHOICE:
            responseForms.append(MultipleChoiceQuestionResponseForm(response=r, allowEdit=False))
    context = {
        'quizAttempt': quizAttempt,
        'forms': responseForms,
    }
    return render(request, 'core/quizAttemptReviewView.html', context)


def quizAttemptResultView(request, attemptId):
    result = Result.objects.filter(
        Q(quizAttempt_id=attemptId, quizAttempt__user_id=request.user.id) |
        Q(quizAttempt_id=attemptId, quizAttempt__quiz__creator_id=request.user.id)
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


def quizAttemptsForQuizView(request, quizId):
    quizAttemptList = QuizAttempt.objects.select_related('user').filter(quiz_id=quizId)
    context = {
        'quizAttemptList': quizAttemptList,
        'quizId': quizId,
    }
    return render(request, 'core/quizAttemptsForQuizView.html', context)


class AttemptedQuizzesView(ListView):
    model = QuizAttempt
    template_name = 'core/attemptedQuizzesView.html'
    context_object_name = 'quizAttemptList'

    def get_queryset(self):
        return QuizAttempt.objects.select_related('quiz__subject').filter(user=self.request.user)
