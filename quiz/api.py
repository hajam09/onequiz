import json
from http import HTTPStatus
from json import JSONDecodeError

from django.db.models import F
from django.http import JsonResponse
from django.urls import reverse
from django.views import View

from onequiz.operations.generalOperations import (
    QuestionAndResponse, QuizAttemptAutomaticMarking, QuizAttemptManualMarking
)
from quiz.models import (
    EssayQuestion, EssayResponse, MultipleChoiceQuestion, MultipleChoiceResponse, QuizAttempt, Topic,
    TrueOrFalseQuestion, TrueOrFalseResponse, Result
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

    def post(self, *args, **kwargs):
        quizId = self.request.GET.get('quizId')
        newQuizAttempt = QuizAttempt.objects.create(user=self.request.user, quiz_id=quizId)
        questionList = newQuizAttempt.quiz.getQuestions()
        newBulkResponseList = []

        for question in questionList:
            if isinstance(question, EssayQuestion):
                newBulkResponseList.append(
                    EssayResponse.objects.create(
                        question_id=question.id,
                        answer=''
                    )
                )
            elif isinstance(question, TrueOrFalseQuestion):
                newBulkResponseList.append(
                    TrueOrFalseResponse.objects.create(
                        question_id=question.id,
                        isChecked=None
                    )
                )
            elif isinstance(question, MultipleChoiceQuestion):
                choiceList = question.choices['choices']
                for item in choiceList:
                    item['isChecked'] = False
                    del item['isCorrect']
                newBulkResponseList.append(
                    MultipleChoiceResponse.objects.create(
                        question_id=question.id,
                        answers={
                            'answers': choiceList
                        }
                    )
                )
            else:
                print('Unknown question type.')
                continue

        newQuizAttempt.status = QuizAttempt.Status.IN_PROGRESS
        newQuizAttempt.responses.add(*newBulkResponseList)
        newQuizAttempt.save()

        response = {
            "success": True,
            "redirectUrl": reverse('quiz:quiz-attempt-view', kwargs={'attemptId': newQuizAttempt.id})
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuizMarkingOccurrenceApiEventVersion1Component(View):

    def put(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.prefetch_related('responses__question').get(id=kwargs.get('id'))
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
        # TODO: FeatureFlag.SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT
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
            responseInstance.essayresponse.answer = put.get('response').get('text')
            responseInstance.essayresponse.save()
        elif put.get('question').get('type') == 'TrueOrFalseQuestion':
            responseInstance.trueorfalseresponse.isChecked = put.get('response').get('selectedOption')
            responseInstance.trueorfalseresponse.save()
        elif put.get('question').get('type') == 'MultipleChoiceQuestion':
            responseInstance.multiplechoiceresponse.answers['answers'] = put.get('response').get('choices')
            responseInstance.multiplechoiceresponse.save()

        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class QuizAttemptQuestionsApiEventVersion1Component(View):

    def get(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.select_related('quiz').prefetch_related(
            'responses__question', 'responses__essayresponse', 'responses__trueorfalseresponse',
            'responses__multiplechoiceresponse'
        ).get(id=kwargs.get('id'))
        questionList = quizAttempt.quiz.getQuestions()
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
        quizAttempt = QuizAttempt.objects.prefetch_related(
            'responses__question', 'responses__essayresponse', 'responses__trueorfalseresponse',
            'responses__multiplechoiceresponse'
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
                    existingResponseObject.essayresponse.answer = response['response']['text']
                    essayResponseObjects.append(existingResponseObject.essayresponse)
            elif response['type'] == 'TrueOrFalseQuestion':
                existingResponseObject = next((o for o in responseList if o.id == response['response']['id']))
                if existingResponseObject is not None:
                    existingResponseObject.trueorfalseresponse.isChecked = response['response']['selectedOption']
                    trueOrFalseResponseObjects.append(existingResponseObject.trueorfalseresponse)
            elif response['type'] == 'MultipleChoiceQuestion':
                existingResponseObject = next((o for o in responseList if o.id == response['response']['id']))
                if existingResponseObject is not None:
                    existingResponseObject.multiplechoiceresponse.answers['answers'] = response['response']['choices']
                    multipleChoiceResponseObjects.append(existingResponseObject.multiplechoiceresponse)
            else:
                continue

        EssayResponse.objects.bulk_update(essayResponseObjects, ['answer'])
        TrueOrFalseResponse.objects.bulk_update(trueOrFalseResponseObjects, ['isChecked'])
        MultipleChoiceResponse.objects.bulk_update(multipleChoiceResponseObjects, ['answers'])

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
