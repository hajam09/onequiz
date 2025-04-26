import random

from django.conf import settings
from django.contrib.auth.models import User
from faker import Faker

from core.models import Quiz, Question
from onequiz.operations import generalOperations

EMAIL_DOMAINS = ["@yahoo", "@gmail", "@outlook", "@hotmail"]
DOMAINS = [".co.uk", ".com", ".co.in", ".net", ".us"]
BOOLEAN = [True, False]


def createUsers(limit=20, maxLimit=20, save=True):
    currentCount = User.objects.count()
    remaining = max(0, maxLimit - currentCount)
    toCreate = min(limit, remaining)

    if toCreate <= 0:
        return User.objects.none()

    if limit == 0 or currentCount > maxLimit:
        return User.objects.all()[:limit]

    BULK_USERS = []
    uniqueEmails = []
    for _ in range(toCreate):
        fake = Faker()
        firstName = fake.unique.first_name()
        lastName = fake.unique.last_name()
        email = f'{firstName.lower()}.{lastName.lower()}{random.choice(EMAIL_DOMAINS)}{random.choice(DOMAINS)}'
        user = User(username=email, email=email, first_name=firstName, last_name=lastName)
        user.set_password(settings.TEST_PASSWORD)
        BULK_USERS.append(user)
        uniqueEmails.append(email)

    if save:
        User.objects.bulk_create(BULK_USERS)
        return User.objects.filter(email__in=uniqueEmails)

    return BULK_USERS


def createUser(save=True):
    userList = createUsers(1, User.objects.count() + 1, save)
    return userList.first() if save else userList[0]


def createQuiz(creator=None, save=True):
    faker = Faker()

    newQuiz = Quiz()
    newQuiz.name = faker.pystr_format()
    newQuiz.description = faker.paragraph()
    newQuiz.subject = random.choice(Quiz.Subject.values)
    newQuiz.topic = faker.pystr_format()
    newQuiz.quizDuration = faker.random_number(digits=2)
    newQuiz.maxAttempt = faker.random_number(digits=1)
    newQuiz.difficulty = random.choice(Quiz.Difficulty.values)
    newQuiz.passMark = faker.random_number(digits=2)
    newQuiz.successText = faker.paragraph()
    newQuiz.failText = faker.paragraph()

    newQuiz.inRandomOrder = random.choice(BOOLEAN)
    newQuiz.answerAtEnd = random.choice(BOOLEAN)
    newQuiz.isExamPaper = random.choice(BOOLEAN)
    newQuiz.isDraft = random.choice(BOOLEAN)
    newQuiz.creator = creator if creator is not None else createUser()

    if save:
        newQuiz.save()
        newQuiz.refresh_from_db()

    return newQuiz


def createRandomQuestions(quiz, numberOfQuestions=None, save=True):
    if numberOfQuestions is None:
        numberOfQuestions = random.randint(5, 10)

    BULK_QUESTIONS = []

    for _ in range(numberOfQuestions):
        questionType = random.choice(Question.Type.values)

        if questionType == Question.Type.ESSAY:
            BULK_QUESTIONS.append(createEssayQuestion(quiz, False))
        elif questionType == Question.Type.TRUE_OR_FALSE:
            BULK_QUESTIONS.append(createTrueOrFalseQuestion(quiz, False))
        elif questionType == Question.Type.MULTIPLE_CHOICE:
            BULK_QUESTIONS.append(createMultipleChoiceQuestionAndAnswers(quiz, False))

    return Question.objects.bulk_create(BULK_QUESTIONS) if save else BULK_QUESTIONS


def createEssayQuestion(quiz, save=True):
    faker = Faker()
    question = Question(
        quiz=quiz,
        figure=None,
        content=faker.paragraph(),
        explanation=faker.paragraph(),
        mark=faker.random_number(digits=2),
        questionType=Question.Type.ESSAY,
        answer=faker.paragraph()
    )

    if save:
        question.save()
    return question


def createTrueOrFalseQuestion(quiz, save=True):
    faker = Faker()
    question = Question(
        quiz=quiz,
        figure=None,
        content=faker.paragraph(),
        explanation=faker.paragraph(),
        mark=faker.random_number(digits=2),
        questionType=Question.Type.TRUE_OR_FALSE,
        trueOrFalse=random.choice(Question.TrueOrFalse.values)
    )

    if save:
        question.save()
    return question


def createMultipleChoiceQuestionAndAnswers(quiz, save=True):
    faker = Faker()
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

    question = Question(
        quiz=quiz,
        figure=None,
        content=faker.paragraph(),
        explanation=faker.paragraph(),
        mark=faker.random_number(digits=2),
        questionType=Question.Type.MULTIPLE_CHOICE,
        choiceOrder=random.choice(Question.ChoiceOrder.values),
        choiceType=choiceType,
        choices={'choices': choices}
    )

    if save:
        question.save()
    return question
