import operator
import os
import random
import re
from functools import reduce

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from core.models import Quiz, Question, Result, Response


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
        'name', 'description', 'url', 'topic',
        'subject__name', 'subject__description',
    ]

    filterList.append(reduce(operator.or_, [Q(**{'deleteFl': False})]))
    if query and query.strip():
        filterList.append(reduce(operator.or_, [Q(**{f'{v}__icontains': query}) for v in attributesToSearch]))

    return Quiz.objects.filter(reduce(operator.and_, filterList)).select_related('subject').distinct()


class QuestionAndResponse:

    def __init__(self, responseList):
        self.responseList = responseList

    def parseResponseMark(self, mark):
        if mark is None:
            return None
        elif mark % 1 == 0:
            return int(mark)
        return mark

    def getResponse(self):
        computedResponseList = []
        for response in self.responseList:
            coreData = {
                'id': response.question.id,
                'figure': response.question.figure.url if bool(response.question.figure) else None,
                'content': response.question.content,
                'explanation': response.question.explanation,
                'mark': response.question.mark,
                'type': response.question.questionType,
            }

            additionalData = {}

            if response.question.questionType == Question.Type.ESSAY:
                additionalData = {
                    'response': {
                        'id': response.pk,
                        'text': response.answer,
                        'mark': self.parseResponseMark(response.mark)
                    }
                }
            elif response.question.questionType == Question.Type.TRUE_OR_FALSE:
                additionalData = {
                    'response': {
                        'id': response.pk,
                        'selectedOption': response.trueSelected,
                        'mark': self.parseResponseMark(response.mark)
                    }
                }
            elif response.question.questionType == Question.Type.MULTIPLE_CHOICE:
                additionalData = {
                    'response': {
                        'id': response.pk,
                        'choices': [
                            {
                                'id': choice['id'],
                                'content': choice['content'],
                                'isChecked': choice['isChecked']
                            }
                            for choice in response.choices['choices']
                        ],
                        'mark': self.parseResponseMark(response.mark)
                    }
                }

            try:
                mergedData = coreData | additionalData
            except TypeError:
                mergedData = {**coreData, **additionalData}
            computedResponseList.append(mergedData)

        return computedResponseList


class QuizAttemptAutomaticMarking:
    def __init__(self, quizAttempt, responseList):
        self.quizAttempt = quizAttempt
        self.responseList = responseList
        self.errors = []
        self.result = None

    def mark(self):
        numberOfCorrectAnswers = 0
        numberOfPartialAnswers = 0
        numberOfWrongAnswers = 0
        totalAwardedMark = 0
        totalQuizMark = 0

        for response in self.responseList:
            awardedMark = 0
            if response.question.questionType == Question.Type.ESSAY:
                self.errors.append('Quiz contains an essay question, which needs manual marking.')
                return False

            elif response.question.questionType == Question.Type.TRUE_OR_FALSE:
                actualAnswer = response.question.trueSelected
                providedAnswer = response.trueSelected
                awardedMark = response.question.mark if actualAnswer == providedAnswer else 0
                if awardedMark == response.question.mark:
                    numberOfCorrectAnswers += 1
                else:
                    numberOfWrongAnswers += 1

            elif response.question.questionType == Question.Type.MULTIPLE_CHOICE:
                actualChoices = response.question.choices['choices']
                providedChoices = response.choices['choices']
                marksPerChoice = round(response.question.mark / len(actualChoices), 2)
                for ac in actualChoices:
                    pc = next((p for p in providedChoices if p['id'] == ac['id']))
                    if pc is not None and ac['isCorrect'] == pc['isChecked']:
                        awardedMark += marksPerChoice

                if awardedMark == response.question.mark:
                    numberOfCorrectAnswers += 1
                elif awardedMark == 0:
                    numberOfWrongAnswers += 1
                else:
                    numberOfPartialAnswers += 1

            totalAwardedMark += awardedMark
            totalQuizMark += response.question.mark
            response.mark = awardedMark

        self.result = Result.objects.create(
            quizAttempt=self.quizAttempt,
            timeSpent=(timezone.now() - self.quizAttempt.createdDttm).seconds,
            numberOfCorrectAnswers=numberOfCorrectAnswers,
            numberOfPartialAnswers=numberOfPartialAnswers,
            numberOfWrongAnswers=numberOfWrongAnswers,
            score=round(totalAwardedMark / totalQuizMark * 100, 2)
        )
        return True


class QuizAttemptManualMarking:
    def __init__(self, quizAttempt, responseList, awardedMarks):
        self.quizAttempt = quizAttempt
        self.responseList = responseList
        self.awardedMarks = awardedMarks
        self.result = None

    def getResponseObject(self, qid, rid):
        return next((r for r in self.responseList if r.question.id == qid and r.id == rid), None)

    def mark(self):
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

        Response.objects.bulk_update(self.responseList, ['mark'])
        self.result = Result(
            quizAttempt=self.quizAttempt,
            timeSpent=(timezone.now() - self.quizAttempt.createdDttm).seconds,
            numberOfCorrectAnswers=numberOfCorrectAnswers,
            numberOfPartialAnswers=numberOfPartialAnswers,
            numberOfWrongAnswers=numberOfWrongAnswers,
            score=round(totalAwardedMark / totalQuizMark * 100, 2)
        )
        return True
