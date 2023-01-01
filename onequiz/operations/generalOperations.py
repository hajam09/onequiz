import operator
import os
import random
import re
from functools import reduce

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from quiz.models import Response, Result, Quiz, EssayResponse, TrueOrFalseResponse, MultipleChoiceResponse


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

        additionalData = (
                self.getEssayQuestionResponse(question) or self.getTrueOrFalseQuestionResponse(question)
                or self.getMultipleChoiceQuestionResponse(question) or {}
        )

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
        response = self.getResponseObject(question)

        try:
            essayResponse = response.essayResponse
        except EssayResponse.DoesNotExist:
            return None

        data = {
            'type': 'EssayQuestion',
            'response': {
                'id': essayResponse.pk,
                'text': essayResponse.answer,
                'mark': self.parseResponseMark(response.mark)
            }
        }
        return data

    def getTrueOrFalseQuestionResponse(self, question):
        response = self.getResponseObject(question)

        try:
            trueOrFalseResponse = response.trueOrFalseResponse
        except TrueOrFalseResponse.DoesNotExist:
            return None

        data = {
            'type': 'TrueOrFalseQuestion',
            'response': {
                'id': trueOrFalseResponse.pk,
                'selectedOption': trueOrFalseResponse.trueSelected,
                'mark': self.parseResponseMark(response.mark)
            }
        }
        return data

    def getMultipleChoiceQuestionResponse(self, question):
        response = self.getResponseObject(question)

        try:
            multipleChoiceResponse = response.multipleChoiceResponse
        except MultipleChoiceResponse.DoesNotExist:
            return None

        data = {
            'type': 'MultipleChoiceQuestion',
            'response': {
                'id': multipleChoiceResponse.pk,
                'choices': [
                    {
                        'id': answer['id'],
                        'content': answer['content'],
                        'isChecked': answer['isChecked']
                    }
                    for answer in multipleChoiceResponse.answers['answers']
                ],
                'mark': self.parseResponseMark(response.mark)
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

            response = self.getResponseObject(item['questionId'], item['responseId'])
            if response is None:
                return False

            response.mark = float(item['awardedMark'])
            if response.mark == response.question.mark:
                numberOfCorrectAnswers += 1
            elif response.mark == 0:
                numberOfWrongAnswers += 1
            else:
                numberOfPartialAnswers += 1

            totalQuizMark += response.question.mark
            totalAwardedMark += response.mark
            updatedObjectList.append(response)

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
            if hasattr(question, 'essayQuestion'):
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
            response = self.getResponseObject(question)
            awardedMark = 0

            if hasattr(question, 'essayQuestion'):
                continue
            elif hasattr(question, 'trueOrFalseQuestion'):
                actualAnswer = question.trueOrFalseQuestion.isCorrect
                providedAnswer = response.trueOrFalseResponse.trueSelected
                awardedMark = question.mark if actualAnswer == providedAnswer else 0
                if awardedMark == question.mark:
                    numberOfCorrectAnswers += 1
                else:
                    numberOfWrongAnswers += 1
            elif hasattr(question, 'multipleChoiceQuestion'):
                actualChoices = question.multipleChoiceQuestion.choices['choices']
                providedChoices = response.multipleChoiceResponse.answers['answers']
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
            response.mark = awardedMark
            responseObjectsList.append(response)

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
