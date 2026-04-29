import random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from faker import Faker

from core.models import Quiz, Question
from onequiz.operations import generalOperations
from settings.models import UserNotificationSettings

BOOLEAN = [True, False]

faker = Faker('en_GB')


def createUsers(count=1):
    hashed_password = make_password('admin')
    users_to_create = []

    for _ in range(count):
        first_name = faker.unique.first_name()
        last_name = faker.unique.last_name()
        email = f'{first_name.lower()}.{last_name.lower()}@{faker.free_email_domain()}'

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
            password=hashed_password
        )
        users_to_create.append(user)

    users = User.objects.bulk_create(users_to_create)
    if count == 1:
        return users[0]
    return users


def createQuiz(creator=None, count=1, save=True):
    quiz = [
        Quiz(
            name=faker.pystr_format(),
            description=faker.paragraph(),
            subject=random.choice(Quiz.Subject.values),
            topic=faker.pystr_format(),
            quizDuration=faker.random_number(digits=2),
            maxAttempt=faker.random_number(digits=1),
            difficulty=random.choice(Quiz.Difficulty.values),
            passMark=faker.random_number(digits=2),
            successText=faker.paragraph(),
            failText=faker.paragraph(),
            inRandomOrder=random.choice(BOOLEAN),
            answerAtEnd=random.choice(BOOLEAN),
            isExamPaper=random.choice(BOOLEAN),
            isDraft=random.choice(BOOLEAN),
            creator=creator if creator is not None else createUsers(1)
        )
        for _ in range(count)
    ]

    quiz = Quiz.objects.bulk_create(quiz) if save else quiz
    if count == 1:
        return quiz[0]
    return quiz


def createEssayQuestion(quiz, count=1, save=True):
    question = [
        Question(
            quiz=quiz,
            figure=None,
            content=faker.paragraph(),
            explanation=faker.paragraph(),
            mark=faker.random_number(digits=2),
            questionType=Question.Type.ESSAY,
            answer=faker.paragraph()
        )
        for _ in range(count)
    ]

    question = Question.objects.bulk_create(question) if save else question
    if count == 1:
        return question[0]
    return question


def createTrueOrFalseQuestion(quiz, count=1, save=True):
    question = [
        Question(
            quiz=quiz,
            figure=None,
            content=faker.paragraph(),
            explanation=faker.paragraph(),
            mark=faker.random_number(digits=2),
            questionType=Question.Type.TRUE_OR_FALSE,
            trueOrFalse=random.choice(Question.TrueOrFalse.values)
        )
        for _ in range(count)
    ]

    question = Question.objects.bulk_create(question) if save else question
    if count == 1:
        return question[0]
    return question


def createMultipleChoiceQuestionAndAnswers(quiz, count=1, save=True):
    questions = []
    for _ in range(count):
        choiceType = random.choice(Question.ChoiceType.values)
        choices = [
            {
                'id': generalOperations.generateRandomString(8),
                'content': faker.paragraph(),
                'isChecked': False if choiceType == Question.ChoiceType.SINGLE else random.choice(BOOLEAN)
            } for _ in range(random.randint(2, 10))
        ]

        if choiceType == Question.ChoiceType.SINGLE:
            random.choice(choices)['isChecked'] = True

        questions.append(
            Question(
                quiz=quiz,
                figure=None,
                content=faker.paragraph(),
                explanation=faker.paragraph(),
                mark=faker.random_number(digits=2),
                questionType=Question.Type.MULTIPLE_CHOICE,
                choiceOrder=random.choice(Question.ChoiceOrder.values),
                choiceType=choiceType,
                choices=choices
            )
        )

    question = Question.objects.bulk_create(questions) if save else questions
    if count == 1:
        return question[0]
    return question


def createRandomQuestions(quiz, count=None, save=True):
    count = count or random.randint(5, 10)
    questions = []

    for _ in range(count):
        questionType = random.choice(Question.Type.values)
        if questionType == Question.Type.ESSAY:
            questions.append(
                createEssayQuestion(quiz, 1, False)
            )
        elif questionType == Question.Type.TRUE_OR_FALSE:
            questions.append(
                createTrueOrFalseQuestion(quiz, 1, False)
            )
        elif questionType == Question.Type.MULTIPLE_CHOICE:
            questions.append(
                createMultipleChoiceQuestionAndAnswers(quiz, 1, False)
            )

    return Question.objects.bulk_create(questions) if save else questions


def createUserNotifications(user, save=True):
    notification = UserNotificationSettings(
        user=user,
        emailOnQuizAttemptSubmitted=random.choice(BOOLEAN),
        emailOnQuizMarked=random.choice(BOOLEAN),
        emailOnPasswordChanged=random.choice(BOOLEAN),
        emailOnAccountSecurityUpdate=random.choice(BOOLEAN),
        emailOnProductUpdates=random.choice(BOOLEAN),
    )

    if save:
        return notification.save()
    return notification
