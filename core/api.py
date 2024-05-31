import json
from http import HTTPStatus

from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views import View
from rest_framework import status
from rest_framework.views import APIView

from core.models import Question, QuizAttempt, Response, Result
from onequiz.operations.featureFlagOperations import featureFlagOperations, FeatureFlagType
from onequiz.operations.generalOperations import (
    QuestionAndResponse, QuizAttemptAutomaticMarking, QuizAttemptManualMarking
)


class QuestionResponseUpdateApiEventVersion1Component(View):

    def put(self, request, *args, **kwargs):
        if not featureFlagOperations.isEnabled(FeatureFlagType.SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT):
            response = {
                'success': False,
                'message': f'Feature flag {FeatureFlagType.SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT.value} not enabled.'
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        put = json.loads(self.request.body)
        quizAttemptId = put.get('quizAttemptId')
        questionId = put.get('question').get('id')
        responseId = put.get('response').get('id')

        if not all([quizAttemptId, questionId, responseId]):
            return Response({'success': False, 'message': 'Invalid data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quizAttempt = QuizAttempt.objects.select_related('quiz').prefetch_related('responses__question').get(
                id=questionId
            )
        except QuizAttempt.DoesNotExist:
            return Response({'success': False, 'message': 'Quiz attempt not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            responseInstance = quizAttempt.responses.get(question_id=questionId, id=responseId)
        except Response.DoesNotExist:
            return Response({'success': False, 'message': 'Response not found.'}, status=status.HTTP_404_NOT_FOUND)

        if put.get('question').get('type') == 'EssayQuestion':
            responseInstance.answer = put.get('response').get('text')
        elif put.get('question').get('type') == 'TrueOrFalseQuestion':
            responseInstance.trueSelected = put.get('response').get('selectedOption')
        elif put.get('question').get('type') == 'MultipleChoiceQuestion':
            responseInstance.choices['choices'] = put.get('response').get('choices')

        responseInstance.save()
        return Response({'success': True}, status=status.HTTP_200_OK)


class QuizAttemptObjectApiEventVersion1Component(APIView):

    def post(self, request, *args, **kwargs):
        quizId = request.GET.get('quizId')
        existingQuizAttempt = QuizAttempt.objects.filter(
            quiz_id=quizId, user=self.request.user, status=QuizAttempt.Status.IN_PROGRESS
        ).first()

        if existingQuizAttempt:
            response = {
                'success': True,
                'message': 'You already have an attempt that is in progress.',
                'redirectUrl': reverse('core:quiz-attempt-view-v1', kwargs={'attemptId': existingQuizAttempt.id})
            }
            return Response(response, status=status.HTTP_200_OK)

        questionsFromQuiz = Question.objects.filter(quizQuestions__id=quizId)
        if not questionsFromQuiz.exists():
            response = {
                'success': False,
                'message': 'No questions found for this quiz. Unable to create an attempt.',
            }
            return Response(response, status=status.HTTP_200_OK)

        bulkResponse = []
        for question in questionsFromQuiz:
            response = Response(question_id=question.id)

            if question.questionType == Question.Type.ESSAY:
                response.answer = ''
            elif question.questionType == Question.Type.TRUE_OR_FALSE:
                response.trueSelected = None
            elif question.questionType == Question.Type.MULTIPLE_CHOICE:
                response.choices = question.cleanAndCloneChoices()
            bulkResponse.append(response)

        with transaction.atomic():
            createdResponses = Response.objects.bulk_create(bulkResponse)
            newQuizAttempt = QuizAttempt.objects.create(
                user=self.request.user, quiz_id=quizId, status=QuizAttempt.Status.IN_PROGRESS
            )
            newQuizAttempt.responses.add(*createdResponses)

        response = {
            'success': True,
            'redirectUrl': reverse('core:quiz-attempt-view-v1', kwargs={'attemptId': newQuizAttempt.id})
        }
        return Response(response, status=status.HTTP_200_OK)


class QuizAttemptObjectApiEventVersion2Component(View):
    def post(self, *args, **kwargs):
        quizAttempt, created = QuizAttempt.objects.get_or_create(
            quiz_id=self.request.GET.get('quizId'),
            user=self.request.user,
            status=QuizAttempt.Status.IN_PROGRESS,
        )
        response = {
            'success': True,
            'redirectUrl': reverse('core:quiz-attempt-view-v2', kwargs={'attemptId': quizAttempt.id})
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuizAttemptQuestionsApiEventVersion1Component(APIView):

    def get(self, request, *args, **kwargs):
        try:
            quizAttempt = QuizAttempt.objects.prefetch_related('responses__question').get(id=kwargs.get('id'))
        except QuizAttempt.DoesNotExist:
            return Response({'success': False, 'message': 'Quiz attempt not found.'}, status=status.HTTP_404_NOT_FOUND)

        responseList = quizAttempt.getResponses()
        computedResponseList = QuestionAndResponse(responseList)

        response = {
            'success': True,
            'data': {
                'questions': computedResponseList.getResponse(),
                'quiz': {
                    'canEdit': quizAttempt.status in [QuizAttempt.Status.NOT_ATTEMPTED, QuizAttempt.Status.IN_PROGRESS]
                }
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def put(self, request, *args, **kwargs):
        try:
            quizAttempt = QuizAttempt.objects.select_related('quiz').get(id=kwargs.get('id'))
        except QuizAttempt.DoesNotExist:
            return Response({'success': False, 'message': 'Quiz attempt not found.'}, status=status.HTTP_404_NOT_FOUND)

        put = json.loads(self.request.body)
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
        return JsonResponse(response={'success': True}, status=HTTPStatus.OK)


class QuizMarkingOccurrenceApiEventVersion1Component(APIView):

    def put(self, request, *args, **kwargs):
        try:
            quizAttempt = QuizAttempt.objects.get(id=kwargs.get('id'))
        except QuizAttempt.DoesNotExist:
            return Response({'success': False, 'message': 'Quiz attempt not found.'}, status=status.HTTP_404_NOT_FOUND)

        put = json.loads(self.request.body)
        responseList = quizAttempt.responses.all().select_related('question')
        awardedMarks = put.get('response', [])

        quizAttemptManualMarking = QuizAttemptManualMarking(quizAttempt, responseList, awardedMarks)

        if quizAttemptManualMarking.mark():
            resultObject = quizAttemptManualMarking.result
            quizAttempt.status = QuizAttempt.Status.MARKED
            resultObject.save()
            quizAttempt.save()

        response = {
            'success': True,
            'redirectUrl': reverse('core:quiz-attempt-result-view', kwargs={'attemptId': quizAttempt.id})
        }
        return JsonResponse(response, status=HTTPStatus.OK)
