import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from core.models import Subject
from onequiz.operations import bakerOperations

BOOLEAN = [True, False]


class Command(BaseCommand):
    help = 'Create Baker Model'

    def handle(self, *args, **kwargs):
        bakerOperations.createUsers()
        bakerOperations.createSubjects()

        allUsers = User.objects.all()
        allSubjects = Subject.objects.all()
        # quizAndQuestions = []

        for i in range(10):
            randomUser = random.choice(allUsers)
            randomSubject = random.choice(allSubjects)

            # quizAndQuestion = {
            #     'quiz': bakerOperations.createQuiz(creator=randomUser, subject=randomSubject, save=False),
            #     'questions': bakerOperations.createRandomQuestions(numberOfQuestions=2, save=False)
            # }
            #
            # quizAndQuestions.append(quizAndQuestion)
            # print(f"Creating quiz: {i} name: {quizAndQuestion['quiz'].name}")

            newQuiz = bakerOperations.createQuiz(creator=randomUser, subject=randomSubject, save=True)
            randomQuestionsList = bakerOperations.createRandomQuestions()
            newQuiz.questions.add(*randomQuestionsList)

        # listOfQuestions = [j for sub in [item['questions'] for item in quizAndQuestions] for j in sub]
        # Question.objects.bulk_create(listOfQuestions, 200)
        #
        # for quizAndQuestion in quizAndQuestions:
        #     quiz = quizAndQuestion['quiz']
        #     quiz.save()
        #
        #     quiz.questions.add(*quizAndQuestion['questions'])
