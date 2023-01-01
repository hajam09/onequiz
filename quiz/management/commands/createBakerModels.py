import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from onequiz.operations import bakerOperations
from quiz.models import Topic

BOOLEAN = [True, False]


class Command(BaseCommand):
    help = 'Create Baker Model'

    def handle(self, *args, **kwargs):
        bakerOperations.createSubjectsAndTopics(1, 1)
        bakerOperations.createUsers()

        allUsers = User.objects.all()
        allTopics = Topic.objects.all()

        for i in range(10):
            randomUser = random.choice(allUsers)
            randomTopic = random.choice(allTopics)
            newQuiz = bakerOperations.createQuiz(creator=randomUser, topic=randomTopic)

            # create three of each questions for this quiz.
            eq1 = bakerOperations.createEssayQuestion().question
            eq2 = bakerOperations.createEssayQuestion().question
            eq3 = bakerOperations.createEssayQuestion().question

            tf1 = bakerOperations.createTrueOrFalseQuestion().question
            tf2 = bakerOperations.createTrueOrFalseQuestion().question
            tf3 = bakerOperations.createTrueOrFalseQuestion().question

            mcq1 = bakerOperations.createMultipleChoiceQuestionAndAnswers(None).question
            mcq2 = bakerOperations.createMultipleChoiceQuestionAndAnswers(None).question
            mcq3 = bakerOperations.createMultipleChoiceQuestionAndAnswers(None).question

            newQuiz.questions.add(*[
                eq1, eq2, eq3,
                tf1, tf2, tf3,
                mcq1, mcq2, mcq3
            ])