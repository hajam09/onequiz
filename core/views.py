import json
import operator
import uuid
from functools import reduce

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import OuterRef, Subquery, Value
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.views.generic import ListView

from core.forms import (
    EssayQuestionCreateForm, MultipleChoiceQuestionCreateForm, TrueOrFalseQuestionCreateForm,
    EssayQuestionUpdateForm, MultipleChoiceQuestionUpdateForm, TrueOrFalseQuestionUpdateForm,
    QuizCreateForm, QuizUpdateForm, EssayQuestionResponseForm, TrueOrFalseQuestionResponseForm,
    MultipleChoiceQuestionResponseForm,
)
from core.models import Quiz, Question, QuizAttempt, Result, Subject, Response
from onequiz.operations import generalOperations
from onequiz.operations.generalOperations import QuizAttemptManualMarking2


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


def quizUpdateView(request, url):
    try:
        quiz = Quiz.objects.select_related('subject').get(url=url)  # creator=request.user
    except Quiz.DoesNotExist:
        raise Http404

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
    try:
        quiz = Quiz.objects.get(url=url, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = EssayQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save()
            quiz.questions.add(question)
            return redirect('core:essay-question-create-view', url=url)
    else:
        form = EssayQuestionCreateForm()

    formTitle = 'Create Essay Question'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizUrl': url,
    }
    return render(request, 'core/essayQuestionTemplateView.html', context)


@login_required
def multipleChoiceQuestionCreateView(request, url):
    try:
        quiz = Quiz.objects.get(url=url, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = MultipleChoiceQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save()
            quiz.questions.add(question)
            return redirect('core:multiple-choice-question-create-view', url=url)
    else:
        form = MultipleChoiceQuestionCreateForm()

    formTitle = 'Create Multiple Choice Question'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizUrl': url,
    }
    return render(request, 'core/multipleChoiceQuestionTemplateView.html', context)


@login_required
def trueOrFalseQuestionCreateView(request, url):
    try:
        quiz = Quiz.objects.get(url=url, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = TrueOrFalseQuestionCreateForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save()
            quiz.questions.add(question)
            return redirect('core:true-or-false-question-create-view', url=url)
    else:
        form = TrueOrFalseQuestionCreateForm()

    formTitle = 'Create True or False Question'

    context = {
        'form': form,
        'formTitle': formTitle,
        'quizUrl': url,
    }
    return render(request, 'core/trueOrFalseQuestionTemplateView.html', context)


@login_required
def bulkQuestionCreateView(request, url):
    try:
        quiz = Quiz.objects.get(url=url, creator=request.user)
    except Quiz.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        bulk_questions = []
        file = request.FILES.get('file')
        if file.content_type == 'application/json':
            for question in json.load(file):
                new_question = Question()

                if 'answer' in question:
                    question_type = Question.Type.ESSAY
                    new_question.answer = question.get('answer')
                elif 'options' in question:
                    question_type = Question.Type.MULTIPLE_CHOICE
                    new_question.choiceOrder = question.get('choice_order')

                    if len(question.get('option_answers')) == 1:
                        new_question.choiceType = Question.ChoiceType.SINGLE
                    else:
                        new_question.choiceType = Question.ChoiceType.MULTIPLE

                    for correct_answer in question.get('option_answers'):
                        if correct_answer not in question.get('options'):
                            messages.error(
                                request,
                                f'''The option(s) provided in option_answers are invalid.
                                Ensure all values in option_answers correspond to the available options'''
                            )

                    choices = [
                        {
                            'id': uuid.uuid4().hex,
                            'content': value,
                            'isChecked': key in question.get('option_answers')
                        }
                        for key, value in question.get('options').items()
                    ]
                    new_question.choices = {'choices': choices}

                elif 'true_or_false' in question:
                    question_type = Question.Type.TRUE_OR_FALSE
                    new_question.trueOrFalse = question.get('true_or_false')
                else:
                    question_type = Question.Type.NONE

                new_question.content = question.get('content')
                new_question.explanation = question.get('explanation')
                new_question.mark = question.get('mark')
                new_question.questionType = question_type
                bulk_questions.append(
                    new_question
                )

            Question.objects.bulk_create(bulk_questions, 20)
            quiz.questions.add(*bulk_questions)
        elif file.content_type == 'text/plain':
            pass

    context = {

    }
    return render(request, 'core/bulkQuestionCreateTemplateView.html', context)


@login_required
def questionUpdateView(request, quizUrl, questionUrl):
    try:
        question = Question.objects.get(
            url=questionUrl, quizQuestions__url=quizUrl, quizQuestions__creator=request.user
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
    try:
        quizAttempt = QuizAttempt.objects.select_related('user', 'quiz__creator').get(url=url)
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
def quizAttemptViewVersion2(request, url):
    quizAttempt = get_object_or_404(QuizAttempt.objects.select_related('user'), url=url)

    if quizAttempt.hasQuizEnded() and quizAttempt.status in quizAttempt.getEditStatues():
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    if not quizAttempt.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    if quizAttempt.getPermissionMode(request.user) == QuizAttempt.Mode.MARK:
        # Quiz creator wants to mark this quiz. Temporarily redirect to quizAttemptSubmissionPreview and mark there.
        return redirect('core:quiz-attempt-submission-preview', url=url)

    ref = request.GET.get('ref', 'next')
    questionIndex = request.GET.get('q', 1)

    questions = cache.get(f'quiz-attempt-v2-{url}')
    if questions is None:
        questions = Question.objects.filter(quizQuestions__id=quizAttempt.quiz_id)
        if quizAttempt.quiz.inRandomOrder:
            questions = questions.order_by('?')
        cache.set(f'quiz-attempt-v2-{url}', questions, quizAttempt.quiz.quizDuration * 60 + 30)
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
            responseObject.trueOrFalse = request.POST.get('trueOrFalse')
        elif respondedQuestionObject.questionType == Question.Type.MULTIPLE_CHOICE:
            optionsKey = next((key for key in request.POST if key.startswith('option')), None)
            checkedOptionsIds = set(request.POST.getlist(optionsKey))
            for choice in responseObject.choices.get('choices'):
                choice['isChecked'] = choice['id'] in checkedOptionsIds

        responseObject.save()

    try:
        questionPaginator = paginator.page(questionIndex)
    except PageNotAnInteger:
        questionPaginator = paginator.page(1)
    except EmptyPage:
        if int(questionIndex) > paginator.num_pages:
            return redirect('core:quiz-attempt-submission-preview', url=url)
        questionPaginator = paginator.page(paginator.num_pages)

    currentQuestion = questionPaginator.object_list[0]
    responseObject, created = Response.objects.select_related('question').get_or_create(
        quizAttemptResponses__in=[quizAttempt], question=currentQuestion
    )
    quizAttempt.responses.add(responseObject.id)

    hasQuizEnded = not quizAttempt.hasQuizEnded()
    if currentQuestion.questionType == Question.Type.ESSAY:
        form = EssayQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    elif currentQuestion.questionType == Question.Type.TRUE_OR_FALSE:
        form = TrueOrFalseQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    elif currentQuestion.questionType == Question.Type.MULTIPLE_CHOICE:
        form = MultipleChoiceQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    else:
        raise Exception('Invalid question type')

    numberOfQuestions = questionPaginator.paginator.page_range.stop - questionPaginator.paginator.page_range.start
    context = {
        'quizAttempt': quizAttempt,
        'questionPaginator': questionPaginator,
        'currentQuestion': currentQuestion,
        'form': form,
        'progress': round((questionPaginator.number / numberOfQuestions) * 100, 0)
    }
    return render(request, 'core/quizAttemptViewVersion2.html', context)


@login_required
def quizAttemptViewVersion3(request, url):
    quizAttempt = get_object_or_404(QuizAttempt.objects.select_related('user'), url=url)

    if quizAttempt.hasQuizEnded() and quizAttempt.status in quizAttempt.getEditStatues():
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    if not quizAttempt.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    if quizAttempt.getPermissionMode(request.user) == QuizAttempt.Mode.MARK:
        # Quiz creator wants to mark this quiz. Temporarily redirect to quizAttemptSubmissionPreview and mark there.
        return redirect('core:quiz-attempt-submission-preview', url=url)

    questions = cache.get(f'quiz-attempt-v3-{url}')
    if questions is None:
        questions = Question.objects.filter(quizQuestions__id=quizAttempt.quiz_id)
        if quizAttempt.quiz.inRandomOrder:
            questions = questions.order_by('?')
        cache.set(f'quiz-attempt-v3-{url}', questions, quizAttempt.quiz.quizDuration * 60 + 30)
    paginator = Paginator(questions, 1)

    questionIndex = request.GET.get('q', 1)

    if request.method == 'POST' and quizAttempt.status != QuizAttempt.Status.SUBMITTED:
        # When there is a POST request, it can mean the user wants to view the next question or the previous question.
        # Determine the index shift based on the navigation direction
        if request.POST.get('ref') == 'next':
            indexShift = -1
        elif request.POST.get('ref') == 'prev':
            indexShift = 1
        else:
            raise Exception('IndexShift not provided in the POST request to determine question index.')

        respondedQuestionIndex = int(questionIndex) + indexShift
        respondedQuestionObject = paginator.page(respondedQuestionIndex).object_list[0]
        responseObject = Response.objects.get(quizAttemptResponses__in=[quizAttempt], question=respondedQuestionObject)

        if respondedQuestionObject.questionType == Question.Type.ESSAY:
            responseObject.answer = request.POST.get('answer')
        elif respondedQuestionObject.questionType == Question.Type.TRUE_OR_FALSE:
            responseObject.trueOrFalse = request.POST.get('trueOrFalse')
        elif respondedQuestionObject.questionType == Question.Type.MULTIPLE_CHOICE:
            optionsKey = next((key for key in request.POST if key.startswith('option')), None)
            checkedOptionsIds = set(request.POST.getlist(optionsKey))
            for choice in responseObject.choices.get('choices'):
                choice['isChecked'] = choice['id'] in checkedOptionsIds

        responseObject.save()
        return redirect(reverse('core:quiz-attempt-view-v3', kwargs={'url': url}) + f'?q={questionIndex}')

    try:
        questionPaginator = paginator.page(questionIndex)
    except PageNotAnInteger:
        questionPaginator = paginator.page(1)
    except EmptyPage:
        if int(questionIndex) > paginator.num_pages:
            return redirect('core:quiz-attempt-submission-preview', url=url)
        questionPaginator = paginator.page(paginator.num_pages)

    currentQuestion = questionPaginator.object_list[0]
    responseObject = Response.objects.select_related('question').get(
        quizAttemptResponses__in=[quizAttempt], question=currentQuestion
    )
    hasQuizEnded = not quizAttempt.hasQuizEnded()
    if currentQuestion.questionType == Question.Type.ESSAY:
        form = EssayQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    elif currentQuestion.questionType == Question.Type.TRUE_OR_FALSE:
        form = TrueOrFalseQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    elif currentQuestion.questionType == Question.Type.MULTIPLE_CHOICE:
        form = MultipleChoiceQuestionResponseForm(response=responseObject, allowEdit=hasQuizEnded, validateMark=False)
    else:
        raise Exception('Invalid question type')

    numberOfQuestions = questionPaginator.paginator.page_range.stop - questionPaginator.paginator.page_range.start
    context = {
        'quizAttempt': quizAttempt,
        'questionPaginator': questionPaginator,
        'currentQuestion': currentQuestion,
        'form': form,
        'progress': round((questionPaginator.number / numberOfQuestions) * 100, 0)
    }
    return render(request, 'core/quizAttemptViewVersion3.html', context)


@login_required
def quizAttemptSubmissionPreview(request, url):
    quizAttempt = get_object_or_404(QuizAttempt.objects.select_related('quiz', 'user'), url=url)

    if quizAttempt.hasQuizEnded() and quizAttempt.status in quizAttempt.getEditStatues():
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])

    if not quizAttempt.hasViewPermission(request.user):
        return HttpResponseForbidden('Forbidden')

    isQuizParticipant = quizAttempt.user == request.user
    # handleQuizAttemptUserActions
    # - > User views all their response.
    # - > User submits their quiz attempt.
    if isQuizParticipant and request.method == 'POST' and 'submitQuiz' in request.POST:
        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save(update_fields=['status'])
        cache.delete(f'quiz-attempt-v3-{url}')
        messages.success(
            request,
            'Your attempt has been submitted successfully, please check later for results.'
        )
        return redirect('core:quiz-attempt-submission-preview', url=url)

    # handleQuizCreatorActions
    # - > User views all the response.
    # - > User marks all the response.

    # Ensure all responses exist
    questions = Question.objects.filter(quizQuestions__id=quizAttempt.quiz_id)
    responsesSubquery = Response.objects.filter(
        quizAttemptResponses=quizAttempt, question_id=OuterRef('pk')
    ).values('id')[:1]
    questionsWithResponses = questions.annotate(response_id=Coalesce(Subquery(responsesSubquery), Value(None)))

    bulkResponses = [
        Response(question=question)
        for question in questionsWithResponses if question.response_id is None
    ]

    if bulkResponses:
        bulkResponseCreate = Response.objects.bulk_create(bulkResponses)
        quizAttempt.responses.add(*bulkResponseCreate)

    responses = Response.objects.filter(
        quizAttemptResponses__in=[quizAttempt]
    ).select_related('question').order_by('question__id')

    responseForms = []
    responseBorders = []
    for response in responses:
        form = None
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

        quizAttemptManualMarking2 = QuizAttemptManualMarking2(quizAttempt, responses)
        quizAttemptManualMarking2.mark()

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
        return QuizAttempt.objects.select_related('quiz__subject').filter(user=self.request.user)
