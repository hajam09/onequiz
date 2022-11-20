import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from faker import Faker

from onequiz.operations import bakerOperations
from quiz.models import Topic

BOOLEAN = [True, False]


class Command(BaseCommand):
    help = 'Create Baker Model'

    def handle(self, *args, **kwargs):
        bakerOperations.createSubjectsAndTopics()
        bakerOperations.createUsers()

        allUsers = User.objects.all()
        allTopics = Topic.objects.all()

        for i in range(10):
            randomUser = random.choice(allUsers)
            randomTopic = random.choice(allTopics)
            newQuiz = bakerOperations.createQuiz(creator=randomUser, topic=randomTopic)

            # create three of each questions for this quiz.
            eq1 = bakerOperations.createEssayQuestion()
            eq2 = bakerOperations.createEssayQuestion()
            eq3 = bakerOperations.createEssayQuestion()

            tf1 = bakerOperations.createTrueOrFalseQuestion()
            tf2 = bakerOperations.createTrueOrFalseQuestion()
            tf3 = bakerOperations.createTrueOrFalseQuestion()

            mcq1 = bakerOperations.createMultipleChoiceQuestionAndAnswers(self.generateAnswerOptions())
            mcq2 = bakerOperations.createMultipleChoiceQuestionAndAnswers(self.generateAnswerOptions())
            mcq3 = bakerOperations.createMultipleChoiceQuestionAndAnswers(self.generateAnswerOptions())

            newQuiz.questions.add(eq1)
            newQuiz.questions.add(eq2)
            newQuiz.questions.add(eq3)

            newQuiz.questions.add(tf1)
            newQuiz.questions.add(tf2)
            newQuiz.questions.add(tf3)

            newQuiz.questions.add(mcq1)
            newQuiz.questions.add(mcq2)
            newQuiz.questions.add(mcq3)

    def generateAnswerOptions(self):
        numberOfAnswersCounter = random.randint(3, 5)
        faker = Faker()
        return [(i, faker.paragraph(), random.choice(BOOLEAN)) for i in range(1, numberOfAnswersCounter, 1)]
