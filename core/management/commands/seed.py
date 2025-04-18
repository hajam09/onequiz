import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from core.models import (
    Question,
    Quiz
)
from onequiz.operations import bakerOperations

BOOLEAN = [True, False]


class Command(BaseCommand):
    help = 'Create Baker Model'
    NUMBER_OF_QUIZ = 300

    def handle(self, *args, **kwargs):
        bakerOperations.createUsers()
        allUsers = list(User.objects.all())

        quizList = [
            bakerOperations.createQuiz(creator=random.choice(allUsers), save=False)
            for _ in range(Command.NUMBER_OF_QUIZ)
        ]

        questionList = [
            bakerOperations.createRandomQuestions(save=False)
            for _ in range(Command.NUMBER_OF_QUIZ)
        ]

        questionAsFlat = [item for sublist in questionList for item in sublist]
        Question.objects.bulk_create(questionAsFlat, batch_size=Command.NUMBER_OF_QUIZ)

        quizzes = Quiz.objects.bulk_create(quizList)
        for quiz, questions in zip(quizzes, questionList):
            quiz.questions.add(*questions)
