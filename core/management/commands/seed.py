import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from faker import Faker

from core.models import (
    Question,
    Quiz,
    QuizAttempt,
    Response,
    Result
)
from onequiz.operations import bakerOperations


class Command(BaseCommand):
    help = 'Create Baker Model'
    NUMBER_OF_QUIZ = 100

    def handle(self, *args, **kwargs):
        bakerOperations.createUsers()
        allUsers = list(User.objects.all())

        quizList = [
            bakerOperations.createQuiz(creator=random.choice(allUsers), save=False)
            for _ in range(Command.NUMBER_OF_QUIZ)
        ]

        questionsList = [
            question
            for quiz in quizList
            for question in bakerOperations.createRandomQuestions(quiz=quiz, save=False)
        ]

        Quiz.objects.bulk_create(quizList)
        Question.objects.bulk_create(questionsList)

        self.additional_seed_data()

    def additional_seed_data(self):
        quizList = Quiz.objects.all()
        allUsers = list(User.objects.all())
        faker = Faker()
        qAttemptBulk = []
        responseBulk = []
        for quiz in quizList:
            qAttempt = QuizAttempt()
            qAttempt.quiz = quiz
            qAttempt.user = random.choice([u for u in allUsers if u.id != quiz.creator.id])
            qAttempt.status = random.choice(QuizAttempt.Status.values)
            qAttemptBulk.append(qAttempt)

            thisQuizQuestions = Question.objects.filter(quiz=quiz)

            for question in thisQuizQuestions:
                rr = Response()
                rr.question = question
                rr.quizAttempt = qAttempt

                if question.questionType == Question.Type.ESSAY:
                    rr.answer = faker.paragraph()
                elif question.questionType == Question.Type.MULTIPLE_CHOICE:
                    rr.choices = question.cloneAndCleanChoices()
                elif question.questionType == Question.Type.TRUE_OR_FALSE:
                    rr.trueOrFalse = random.choice(Question.TrueOrFalse.values)

                responseBulk.append(rr)

        QuizAttempt.objects.bulk_create(qAttemptBulk)
        Response.objects.bulk_create(responseBulk)

        resultBulk = []
        submittedAttempts = QuizAttempt.objects.filter(status=QuizAttempt.Status.SUBMITTED)
        for submittedAttempt in submittedAttempts:
            result = Result()
            result.quizAttempt = submittedAttempt
            result.timeSpent = faker.random_number(digits=3)
            result.score = faker.random_number(digits=2)
            result.numberOfCorrectAnswers = faker.random_number(digits=1)
            result.numberOfPartialAnswers = faker.random_number(digits=1)
            result.numberOfWrongAnswers = faker.random_number(digits=1)
            resultBulk.append(result)

            submittedAttempt.status = QuizAttempt.Status.MARKED

        Result.objects.bulk_create(resultBulk)
        QuizAttempt.objects.bulk_update(submittedAttempts, fields=['status'])
