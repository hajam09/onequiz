import operator
import random
import uuid
from functools import reduce
from string import (
    ascii_letters,
    digits
)

from django.db.models import (
    F,
    Case,
    When,
    Value,
    Sum,
    IntegerField
)
from django.db.models import Q
from django.utils import timezone

from core.models import (
    Quiz,
    Question,
    Result,
    Response
)


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


def generateRandomString(length):
    if length >= 6:
        return uuid.uuid4().hex[:length]
    return ''.join(random.choice(ascii_letters + digits) for _ in range(length))


def performComplexQuizSearch(query, filterList=None):
    filterList = filterList or []
    attributesToSearch = [
        'name', 'description', 'url', 'topic', 'subject'
    ]

    filterList.append(reduce(operator.or_, [Q(**{'deleteFl': False})]))
    if query and query.strip():
        filterList.append(reduce(operator.or_, [Q(**{f'{v}__icontains': query}) for v in attributesToSearch]))

    return Quiz.objects.filter(reduce(operator.and_, filterList)).distinct()


class QuizAttemptAutomaticMarking:
    def __init__(self, quizAttempt, responses):
        self.quizAttempt = quizAttempt
        self.responses = responses

    def mark(self):
        numberOfCorrectAnswers = 0
        numberOfPartialAnswers = 0
        numberOfWrongAnswers = 0
        totalAwardedMark = 0
        totalQuizMark = 0

        for response in self.responses:
            awardedMark = 0
            if response.question.questionType == Question.Type.ESSAY:
                return False

            elif response.question.questionType == Question.Type.TRUE_OR_FALSE:
                actualAnswer = response.question.trueOrFalse
                selectedAnswer = response.trueOrFalse
                awardedMark = response.question.mark if actualAnswer == selectedAnswer else 0
                if awardedMark == response.question.mark:
                    numberOfCorrectAnswers += 1
                else:
                    numberOfWrongAnswers += 1

            elif response.question.questionType == Question.Type.MULTIPLE_CHOICE:
                actualChoices = sorted(response.question.choices['choices'], key=lambda x: x['id'])
                selectedChoices = sorted(response.choices['choices'], key=lambda x: x['id'])

                if response.question.choiceType == Question.ChoiceType.SINGLE:
                    awardedMark = response.question.mark if actualChoices == selectedChoices else 0
                else:
                    marksPerChoice = round(response.question.mark / len(actualChoices), 2)
                    for ac in actualChoices:
                        sc = next((s for s in selectedChoices if s['id'] == ac['id']))
                        if sc is not None and ac['isChecked'] == sc['isChecked']:
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
        Response.objects.bulk_update(self.responses, ['mark'])
        return True


class QuizAttemptManualMarking:
    def __init__(self, quizAttempt, responses):
        self.quizAttempt = quizAttempt
        self.responses = responses
        self.result = None

    def mark(self):
        responses = self.responses.annotate(
            # Mark comparison for correctness, partial correctness, or wrong answers
            is_correct=Case(
                When(mark=F('question__mark'), then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            is_wrong=Case(
                When(mark=Value(0), then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            is_partial=Case(
                When(mark__gt=Value(0), mark__lt=F('question__mark'), then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
        )

        aggregatedResults = responses.aggregate(
            numberOfCorrectAnswers=Sum('is_correct'),
            numberOfPartialAnswers=Sum('is_partial'),
            numberOfWrongAnswers=Sum('is_wrong'),
            totalQuizMark=Sum('question__mark'),
            totalAwardedMark=Sum('mark')
        )

        # Calculate the score as a percentage
        totalQuizMark = aggregatedResults['totalQuizMark']
        totalAwardedMark = aggregatedResults['totalAwardedMark']
        if totalQuizMark > 0:
            score = round(totalAwardedMark / totalQuizMark * 100, 2)
        else:
            score = 0.0

        # Now, save the result
        self.result, created = Result.objects.get_or_create(
            quizAttempt=self.quizAttempt,
            defaults={
                'numberOfCorrectAnswers': aggregatedResults['numberOfCorrectAnswers'],
                'numberOfPartialAnswers': aggregatedResults['numberOfPartialAnswers'],
                'numberOfWrongAnswers': aggregatedResults['numberOfWrongAnswers'],
                'score': score
            }
        )
