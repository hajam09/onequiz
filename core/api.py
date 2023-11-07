import json
from http import HTTPStatus
from json import JSONDecodeError

from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View

from core.models import Question, QuizAttempt, Response, Result
from onequiz.operations.featureFlagOperations import featureFlagOperations, FeatureFlagType
from onequiz.operations.generalOperations import (
    QuestionAndResponse, QuizAttemptAutomaticMarking, QuizAttemptManualMarking
)


class QuizAttemptObjectApiEventVersion1Component(View):
    def post(self, *args, **kwargs):
        quizId = self.request.GET.get('quizId')
        existingQuizAttempt = QuizAttempt.objects.filter(
            quiz_id=quizId, user=self.request.user, status=QuizAttempt.Status.IN_PROGRESS
        ).first()

        if existingQuizAttempt is not None:
            response = {
                "success": True,
                "message": "You already have an attempt that is in progress.",
                "redirectUrl": reverse('core:quiz-attempt-view', kwargs={'attemptId': existingQuizAttempt.id})
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        questionsFromQuiz = Question.objects.filter(quizQuestions__id=quizId)
        if not questionsFromQuiz:
            response = {
                "success": False,
                "message": "No questions found for this quiz. Unable to create an attempt.",
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        BULK_RESPONSE_LIST = []
        for question in questionsFromQuiz:
            response = Response()
            response.question_id = question.id

            if question.questionType == Question.Type.ESSAY:
                response.answer = ''

            if question.questionType == Question.Type.TRUE_OR_FALSE:
                response.trueSelected = None

            if question.questionType == Question.Type.MULTIPLE_CHOICE:
                choiceList = question.choices['choices']
                for item in choiceList:
                    item['isChecked'] = False
                    del item['isCorrect']

                response.choices = {'choices': choiceList}

            BULK_RESPONSE_LIST.append(response)

        with transaction.atomic():
            Response.objects.bulk_create(BULK_RESPONSE_LIST)
            newQuizAttempt = QuizAttempt.objects.create(
                user=self.request.user, quiz_id=quizId, status=QuizAttempt.Status.IN_PROGRESS
            )
            newQuizAttempt.responses.add(*BULK_RESPONSE_LIST)

        response = {
            "success": True,
            "redirectUrl": reverse('core:quiz-attempt-view', kwargs={'attemptId': newQuizAttempt.id})
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuizAttemptQuestionsApiEventVersion1Component(View):
    def get(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.prefetch_related('responses__question').get(id=kwargs.get('id'))
        responseList = quizAttempt.getResponses()
        computedResponseList = QuestionAndResponse(responseList)

        response = {
            "success": True,
            "data": {
                "questions": computedResponseList.getResponse(),
                "quiz": {
                    "canEdit": quizAttempt.status in [QuizAttempt.Status.NOT_ATTEMPTED, QuizAttempt.Status.IN_PROGRESS]
                }
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def put(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.select_related('quiz').get(id=kwargs.get('id'))
        try:
            put = json.loads(self.request.body)
        except JSONDecodeError:
            put = json.loads(self.request.body.decode().replace('"', "'").replace("'", '"'))

        userResponse = put.get('response', [])
        responseList = quizAttempt.responses.all().select_related('question')

        for response in userResponse:
            existingResponseObject = next((o for o in responseList if o.id == response['response']['id']), None)
            if response['type'] == 'EssayQuestion' and existingResponseObject is not None:
                existingResponseObject.answer = response['response']['text']

            elif response['type'] == 'MultipleChoiceQuestion' and existingResponseObject is not None:
                existingResponseObject.choices['choices'] = response['response']['choices']

            elif response['type'] == 'TrueOrFalseQuestion' and existingResponseObject is not None:
                existingResponseObject.trueSelected = response['response']['selectedOption']

        quizAttemptAutomaticMarking = QuizAttemptAutomaticMarking(quizAttempt, responseList)
        if quizAttemptAutomaticMarking.mark():
            quizAttempt.status = QuizAttempt.Status.MARKED
        else:
            quizAttempt.status = QuizAttempt.Status.SUBMITTED
            Result.objects.create(
                quizAttempt=quizAttempt,
                timeSpent=(timezone.now() - quizAttempt.createdDttm).seconds,
                numberOfCorrectAnswers=0,
                numberOfPartialAnswers=0,
                numberOfWrongAnswers=0,
                score=0.00
            )

        quizAttempt.save()
        Response.objects.bulk_update(
            quizAttemptAutomaticMarking.responseList, ['answer', 'choices', 'trueSelected', 'mark']
        )
        response = {
            "success": True,
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuizMarkingOccurrenceApiEventVersion1Component(View):

    def put(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.get(id=kwargs.get('id'))

        try:
            put = json.loads(self.request.body)
        except JSONDecodeError:
            put = json.loads(self.request.body.decode().replace('"', "'").replace("'", '"'))

        responseList = quizAttempt.responses.all().select_related('question')
        awardedMarks = put.get('response', [])

        quizAttemptManualMarking = QuizAttemptManualMarking(quizAttempt, responseList, awardedMarks)

        if quizAttemptManualMarking.mark():
            resultObject = quizAttemptManualMarking.result
            quizAttempt.status = QuizAttempt.Status.MARKED
            resultObject.save()
            quizAttempt.save()

        response = {
            "success": True,
            "redirectUrl": reverse('core:quiz-attempt-result-view', kwargs={'attemptId': quizAttempt.id})
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuestionResponseUpdateApiEventVersion1Component(View):
    def put(self, *args, **kwargs):

        if not featureFlagOperations.isEnabled(FeatureFlagType.SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT):
            response = {
                "success": False,
                "message": f'Feature flag {FeatureFlagType.SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT.value} not enabled.'
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        try:
            put = json.loads(self.request.body)
        except JSONDecodeError:
            put = json.loads(self.request.body.decode().replace('"', "'").replace("'", '"'))

        qaid = put.get('quizAttemptId')
        qid = put.get('question').get('id')
        rid = put.get('response').get('id')

        quizAttempt = QuizAttempt.objects.select_related().prefetch_related('responses__question').get(id=qaid)
        responseList = quizAttempt.responses.all()
        responseInstance = next((r for r in responseList if r.question.id == qid and r.id == rid), None)

        if put.get('question').get('type') == 'EssayQuestion':
            responseInstance.answer = put.get('response').get('text')
        elif put.get('question').get('type') == 'TrueOrFalseQuestion':
            responseInstance.trueSelected = put.get('response').get('selectedOption')
        elif put.get('question').get('type') == 'MultipleChoiceQuestion':
            responseInstance.choices['choices'] = put.get('response').get('choices')

        responseInstance.save()
        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)
