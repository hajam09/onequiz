import operator
import os
import random
import re
from functools import reduce

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from quiz.models import EssayQuestion, MultipleChoiceQuestion, TrueOrFalseQuestion, Response, Result, Quiz


def isPasswordStrong(password):
    if len(password) < 8:
        return False

    if not any(letter.isalpha() for letter in password):
        return False

    if not any(capital.isupper() for capital in password):
        return False

    if not any(number.isdigit() for number in password):
        return False

    return True


def getRandomAvatar():
    return "avatars/" + random.choice(os.listdir(os.path.join(settings.MEDIA_ROOT, "avatars/")))


def deleteImage(imageField):
    if imageField is None:
        return

    existingImage = os.path.join(settings.MEDIA_ROOT, imageField.name)
    try:
        if os.path.exists(existingImage) and "/media/avatars/" not in imageField.url:
            os.remove(existingImage)
    except ValueError:
        pass


def parseStringToUrl(link):
    link = re.sub('\s+', '-', link).lower()
    link = ''.join(letter for letter in link if letter.isalnum() or letter == '-')
    return link


def performComplexQuizSearch(query, filterList=None):
    filterList = filterList or []
    attributesToSearch = [
        'name', 'description', 'url',
        'topic__name', 'topic__description',
        'topic__subject__name', 'topic__subject__description'
    ]

    filterList.append(reduce(operator.or_, [Q(**{'deleteFl': False})]))
    if query and query.strip():
        filterList.append(reduce(operator.or_, [Q(**{f'{v}__icontains': query}) for v in attributesToSearch]))

    return Quiz.objects.filter(reduce(operator.and_, filterList)).select_related('topic__subject').distinct()


class QuestionAndResponse:

    def __init__(self, questionList, responseList):
        self.questionList = questionList
        self.responseList = responseList

    def getResponse(self):
        computedResponseList = [
            self.getResponseForQuestion(question) for question in self.questionList
        ]
        return computedResponseList

    def getResponseForQuestion(self, question):
        data = {
            'id': question.id,
            'figure': question.figure.url if bool(question.figure) else None,
            'content': question.content,
            'explanation': question.explanation,
            'mark': question.mark,
        }

        additionalData = {}
        if isinstance(question, EssayQuestion):
            additionalData = self.getEssayQuestionResponse(question)
        elif isinstance(question, TrueOrFalseQuestion):
            additionalData = self.getTrueOrFalseQuestionResponse(question)
        elif isinstance(question, MultipleChoiceQuestion):
            additionalData = self.getMultipleChoiceQuestionResponse(question)
        else:
            pass

        try:
            mergedData = data | additionalData
        except TypeError:
            mergedData = {**data, **additionalData}

        return mergedData

    def getResponseObject(self, question):
        return next((o for o in self.responseList if o.question.id == question.id))

    def parseResponseMark(self, mark):
        if mark is None:
            return None
        elif mark % 1 == 0:
            return int(mark)
        return mark

    def getEssayQuestionResponse(self, question):
        responseObject = self.getResponseObject(question)
        data = {
            'type': 'EssayQuestion',
            'response': {
                'id': responseObject.essayresponse.id,
                'text': responseObject.essayresponse.answer,
                'mark': self.parseResponseMark(responseObject.essayresponse.mark)
            }
        }
        return data

    def getTrueOrFalseQuestionResponse(self, question):
        responseObject = self.getResponseObject(question)
        data = {
            'type': 'TrueOrFalseQuestion',
            'response': {
                'id': responseObject.trueorfalseresponse.id,
                'selectedOption': responseObject.trueorfalseresponse.isChecked,
                'mark': self.parseResponseMark(responseObject.trueorfalseresponse.mark)
            }
        }
        return data

    def getMultipleChoiceQuestionResponse(self, question):
        responseObject = self.getResponseObject(question)
        data = {
            'type': 'MultipleChoiceQuestion',
            'response': {
                'id': responseObject.multiplechoiceresponse.id,
                'choices': [
                    {
                        'id': answer['id'],
                        'content': answer['content'],
                        'isChecked': answer['isChecked']
                    }
                    for answer in responseObject.multiplechoiceresponse.answers['answers']
                ],
                'mark': self.parseResponseMark(responseObject.multiplechoiceresponse.mark)
            }
        }
        return data


class QuizAttemptManualMarking:
    def __init__(self, quizAttempt, questionList, responseList, awardedMarks):
        self.quizAttempt = quizAttempt
        self.questionList = questionList
        self.responseList = responseList
        self.awardedMarks = awardedMarks
        self.result = None

    def getResponseObject(self, qid, rid):
        return next((o for o in self.responseList if o.question.id == qid and o.id == rid), None)

    def mark(self):
        updatedObjectList = []
        numberOfCorrectAnswers = 0
        numberOfPartialAnswers = 0
        numberOfWrongAnswers = 0
        totalAwardedMark = 0
        totalQuizMark = 0

        for item in self.awardedMarks:
            if not ('questionId' in item and 'responseId' in item and 'awardedMark' in item):
                return False

            responseObject = self.getResponseObject(item['questionId'], item['responseId'])
            if responseObject is None:
                return False

            responseObject.mark = float(item['awardedMark'])
            if responseObject.mark == responseObject.question.mark:
                numberOfCorrectAnswers += 1
            elif responseObject.mark == 0:
                numberOfWrongAnswers += 1
            else:
                numberOfPartialAnswers += 1

            totalQuizMark += responseObject.question.mark
            totalAwardedMark += responseObject.mark
            updatedObjectList.append(responseObject)

        Response.objects.bulk_update(updatedObjectList, ['mark'])
        self.result = Result(
            quizAttempt=self.quizAttempt,
            timeSpent=(timezone.now() - self.quizAttempt.createdDttm).seconds,
            numberOfCorrectAnswers=numberOfCorrectAnswers,
            numberOfPartialAnswers=numberOfPartialAnswers,
            numberOfWrongAnswers=numberOfWrongAnswers,
            score=round(totalAwardedMark / totalQuizMark * 100, 2)
        )
        return True


class QuizAttemptAutomaticMarking:

    def __init__(self, quizAttempt, questionList, responseList):
        self.quizAttempt = quizAttempt
        self.questionList = questionList
        self.responseList = responseList
        self.errors = []
        self.result = None

    def requiresManualMarking(self):
        # any(isinstance(question, EssayQuestion) for question in self.questionList)
        for question in self.questionList:
            if isinstance(question, EssayQuestion):
                return True
        return False

    def getResponseObject(self, question):
        return next((o for o in self.responseList if o.question.id == question.id))

    def mark(self):
        if self.requiresManualMarking():
            self.errors.append('Quiz contains an essay question, which needs manual marking.')
            return False

        responseObjectsList = []
        numberOfCorrectAnswers = 0
        numberOfPartialAnswers = 0
        numberOfWrongAnswers = 0
        totalAwardedMark = 0
        totalQuizMark = 0

        for question in self.questionList:
            responseObject = self.getResponseObject(question)
            awardedMark = 0

            if isinstance(question, EssayQuestion):
                continue
            elif isinstance(question, TrueOrFalseQuestion):
                actualAnswer = question.isCorrect
                providedAnswer = responseObject.trueorfalseresponse.isChecked
                awardedMark = question.mark if actualAnswer == providedAnswer else 0
                if awardedMark == question.mark:
                    numberOfCorrectAnswers += 1
                else:
                    numberOfWrongAnswers += 1
            elif isinstance(question, MultipleChoiceQuestion):
                actualChoices = question.choices['choices']
                providedChoices = responseObject.multiplechoiceresponse.answers['answers']
                marksPerChoice = round(question.mark / len(actualChoices), 2)
                for ac in actualChoices:
                    pc = next((p for p in providedChoices if p['id'] == ac['id']))
                    if pc is not None and ac['isCorrect'] == pc['isChecked']:
                        awardedMark += marksPerChoice

                if awardedMark == question.mark:
                    numberOfCorrectAnswers += 1
                elif awardedMark == 0:
                    numberOfWrongAnswers += 1
                else:
                    numberOfPartialAnswers += 1

            totalAwardedMark += awardedMark
            totalQuizMark += question.mark
            responseObject.mark = awardedMark
            responseObjectsList.append(responseObject)

        self.result = Result.objects.create(
            quizAttempt=self.quizAttempt,
            timeSpent=(timezone.now() - self.quizAttempt.createdDttm).seconds,
            numberOfCorrectAnswers=numberOfCorrectAnswers,
            numberOfPartialAnswers=numberOfPartialAnswers,
            numberOfWrongAnswers=numberOfWrongAnswers,
            score=round(totalAwardedMark / totalQuizMark * 100, 2)
        )

        Response.objects.bulk_update(responseObjectsList, ['mark'])
        return True
