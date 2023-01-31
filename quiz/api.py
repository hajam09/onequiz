import json
from http import HTTPStatus
from json import JSONDecodeError
from threading import Thread

from django.db.models import F
from django.http import JsonResponse
from django.urls import reverse
from django.views import View

from onequiz.operations.featureFlagOperations import featureFlagOperations, FeatureFlagType
from onequiz.operations.generalOperations import (
    QuestionAndResponse, QuizAttemptAutomaticMarking, QuizAttemptManualMarking
)
from quiz.models import (
    EssayResponse, MultipleChoiceResponse, QuizAttempt, Topic, TrueOrFalseResponse, Result, Response, Quiz
)


class TopicObjectApiEventVersion1Component(View):
    def get(self, *args, **kwargs):
        topics = Topic.objects.filter(**self.request.GET.dict()).annotate(
            _id=F('id'), _name=F('name'), _description=F('description')
        ).values('id', 'name', 'description')

        response = {
            "success": True,
            "data": {
                "topics": list(topics)
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuizAttemptObjectApiEventVersion1Component(View):

    def createResponseModels(self, quizAttempt, questionList):
        responseList = []
        essayResponseList = []
        trueOrFalseQuestionList = []
        multipleChoiceQuestionList = []

        for question in questionList:
            response = Response(question_id=question.id)
            responseList.append(response)

            if hasattr(question, 'essayQuestion'):
                essayResponseList.append(
                    EssayResponse(response=response, answer='')
                )
            elif hasattr(question, 'trueOrFalseQuestion'):
                trueOrFalseQuestionList.append(
                    TrueOrFalseResponse(response=response, trueSelected=None)
                )
            elif hasattr(question, 'multipleChoiceQuestion'):
                choiceList = question.multipleChoiceQuestion.choices['choices']
                for item in choiceList:
                    item['isChecked'] = False
                    del item['isCorrect']
                multipleChoiceQuestionList.append(
                    MultipleChoiceResponse(response=response, answers={'answers': choiceList})
                )
            else:
                print('Unknown question type.')
                continue

        Response.objects.bulk_create(responseList)
        EssayResponse.objects.bulk_create(essayResponseList)
        TrueOrFalseResponse.objects.bulk_create(trueOrFalseQuestionList)
        MultipleChoiceResponse.objects.bulk_create(multipleChoiceQuestionList)
        quizAttempt.responses.add(*responseList)
        return

    def post(self, *args, **kwargs):
        quizId = self.request.GET.get('quizId')
        existingQuizAttempt = QuizAttempt.objects.filter(
            quiz_id=quizId, user=self.request.user, status=QuizAttempt.Status.IN_PROGRESS
        )
        if existingQuizAttempt.exists():
            response = {
                "success": True,
                "message": "You already have an attempt that is in progress.",
                "redirectUrl": reverse('quiz:quiz-attempt-view', kwargs={'attemptId': existingQuizAttempt[0].id})
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        quiz = Quiz.objects.prefetch_related(
            'questions__essayQuestion', 'questions__trueOrFalseQuestion', 'questions__multipleChoiceQuestion'
        ).get(id=quizId)
        newQuizAttempt = QuizAttempt.objects.create(user=self.request.user, quiz_id=quiz.id)
        questionList = quiz.getQuestions()

        self.createResponseModels(newQuizAttempt, questionList)
        newQuizAttempt.status = QuizAttempt.Status.IN_PROGRESS
        newQuizAttempt.save()

        response = {
            "success": True,
            "redirectUrl": reverse('quiz:quiz-attempt-view', kwargs={'attemptId': newQuizAttempt.id})
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuizMarkingOccurrenceApiEventVersion1Component(View):

    def put(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.select_related('quiz').prefetch_related(
            'responses__question', 
        ).get(id=kwargs.get('id'))
        try:
            put = json.loads(self.request.body)
        except JSONDecodeError:
            put = json.loads(self.request.body.decode().replace('"', "'").replace("'", '"'))

        questionList = quizAttempt.quiz.getQuestions()
        responseList = quizAttempt.responses.all()
        awardedMarks = put.get('response', [])
        quizAttemptManualMarking = QuizAttemptManualMarking(quizAttempt, questionList, responseList, awardedMarks)

        if quizAttemptManualMarking.mark():
            resultObject = quizAttemptManualMarking.result
            resultObject.versionNo = Result.objects.filter(quizAttempt=quizAttempt).count() + 1
            quizAttempt.status = QuizAttempt.Status.MARKED
            resultObject.save()
            quizAttempt.save()

        response = {
            "success": True,
            "redirectUrl": reverse('quiz:quiz-attempt-result-view', kwargs={'attemptId': quizAttempt.id})
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
            responseInstance.essayResponse.answer = put.get('response').get('text')
            responseInstance.essayResponse.save()
        elif put.get('question').get('type') == 'TrueOrFalseQuestion':
            responseInstance.trueOrFalseResponse.trueSelected = put.get('response').get('selectedOption')
            responseInstance.trueOrFalseResponse.save()
        elif put.get('question').get('type') == 'MultipleChoiceQuestion':
            responseInstance.multipleChoiceResponse.answers['answers'] = put.get('response').get('choices')
            responseInstance.multipleChoiceResponse.save()

        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuizAttemptQuestionsApiEventVersion1Component(View):

    def get(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.prefetch_related(
            'responses__essayResponse', 'responses__trueOrFalseResponse', 'responses__multipleChoiceResponse',
            'responses__question',
        ).get(id=kwargs.get('id'))
        questionList = quizAttempt.quiz.getQuestions(quizAttempt.quiz.inRandomOrder)
        responseList = quizAttempt.responses.all()
        computedResponseList = QuestionAndResponse(questionList, responseList)

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
        quizAttempt = QuizAttempt.objects.select_related('quiz').prefetch_related(
            'responses__essayResponse', 'responses__trueOrFalseResponse', 'responses__multipleChoiceResponse'
        ).get(id=kwargs.get('id'))

        try:
            put = json.loads(self.request.body)
        except JSONDecodeError:
            put = json.loads(self.request.body.decode().replace('"', "'").replace("'", '"'))

        userResponse = put.get('response', [])
        responseList = quizAttempt.responses.all()

        essayResponseObjects = []
        trueOrFalseResponseObjects = []
        multipleChoiceResponseObjects = []

        for response in userResponse:
            if response['type'] == 'EssayQuestion':
                existingResponseObject = next((o for o in responseList if o.id == response['response']['id']))
                if existingResponseObject is not None:
                    existingResponseObject.essayResponse.answer = response['response']['text']
                    essayResponseObjects.append(existingResponseObject.essayResponse)
            elif response['type'] == 'TrueOrFalseQuestion':
                existingResponseObject = next((o for o in responseList if o.id == response['response']['id']))
                if existingResponseObject is not None:
                    existingResponseObject.trueOrFalseResponse.trueSelected = response['response']['selectedOption']
                    trueOrFalseResponseObjects.append(existingResponseObject.trueOrFalseResponse)
            elif response['type'] == 'MultipleChoiceQuestion':
                existingResponseObject = next((o for o in responseList if o.id == response['response']['id']))
                if existingResponseObject is not None:
                    existingResponseObject.multipleChoiceResponse.answers['answers'] = response['response']['choices']
                    multipleChoiceResponseObjects.append(existingResponseObject.multipleChoiceResponse)
            else:
                continue

        EssayResponse.objects.bulk_update(essayResponseObjects, ['answer'])
        TrueOrFalseResponse.objects.bulk_update(trueOrFalseResponseObjects, ['trueSelected'])
        MultipleChoiceResponse.objects.bulk_update(multipleChoiceResponseObjects, ['answers'])

        # TODO: Optimize when automatic marking is enabled.
        quizAttemptAutomaticMarking = QuizAttemptAutomaticMarking(quizAttempt, quizAttempt.quiz.getQuestions(), responseList)
        if quizAttemptAutomaticMarking.mark():
            quizAttempt.status = QuizAttempt.Status.MARKED
        else:
            quizAttempt.status = QuizAttempt.Status.SUBMITTED

        quizAttempt.save()

        response = {
            "success": True,
        }
        return JsonResponse(response, status=HTTPStatus.OK)
