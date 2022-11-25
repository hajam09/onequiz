import json
from http import HTTPStatus

from django.db.models import F
from django.http import JsonResponse, QueryDict
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from onequiz.operations.generalOperations import QuestionAndResponse
from quiz.models import (
    EssayQuestion, EssayResponse, MultipleChoiceQuestion, MultipleChoiceResponse, QuizAttempt, Topic,
    TrueOrFalseQuestion, TrueOrFalseResponse
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


@method_decorator(csrf_exempt, name='dispatch')
class QuizAttemptQuestionsApiEventVersion1Component(View):

    def get(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.select_related('quiz', 'user').prefetch_related(
            'responses__question'
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

    def post(self, *args, **kwargs):
        quizAttempt = QuizAttempt.objects.get(id=kwargs.get('id'))
        queryDict = QueryDict('', mutable=True)
        queryDict.update(json.loads(self.request.body.decode()))
        userResponse = queryDict.get('response', [])
        responseList = quizAttempt.responses.all()

        for response in userResponse:
            if response['type'] == 'EssayQuestion':
                existingResponseObject = next((o for o in responseList if o.id == response['response']['id']))
                if existingResponseObject is not None:
                    existingResponseObject.essayresponse.answer = response['response']['text']
                    existingResponseObject.essayresponse.save()
            elif response['type'] == 'TrueOrFalseQuestion':
                existingResponseObject = next((o for o in responseList if o.id == response['response']['id']))
                if existingResponseObject is not None:
                    existingResponseObject.trueorfalseresponse.isChecked = response['response']['selectedOption']
                    existingResponseObject.trueorfalseresponse.save()
            elif response['type'] == 'MultipleChoiceQuestion':
                existingResponseObject = next((o for o in responseList if o.id == response['response']['id']))
                if existingResponseObject is not None:
                    existingResponseObject.multiplechoiceresponse.answers['answers'] = response['response']['choices']
                    existingResponseObject.multiplechoiceresponse.save()
            else:
                pass

        quizAttempt.status = QuizAttempt.Status.SUBMITTED
        quizAttempt.save()

        response = {
            "success": True,
        }
        return JsonResponse(response, status=HTTPStatus.OK)
