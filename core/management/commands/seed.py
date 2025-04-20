import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from core.models import (
    Question,
    Quiz
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
