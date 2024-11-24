import random
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from faker import Faker

from core.models import Subject, Quiz, Question

EMAIL_DOMAINS = ["@yahoo", "@gmail", "@outlook", "@hotmail"]
DOMAINS = [".co.uk", ".com", ".co.in", ".net", ".us"]
BOOLEAN = [True, False]


def createUsers(limit=20, maxLimit=20, save=True):
    currentCount = User.objects.count()
    remaining = maxLimit - currentCount

    if limit == 0 or currentCount > maxLimit:
        return User.objects.all()[:limit]

    BULK_USERS = []
    uniqueEmails = []
    for _ in range(remaining):
        fake = Faker()
        firstName = fake.unique.first_name()
        lastName = fake.unique.last_name()
        email = firstName.lower() + '.' + lastName.lower() + random.choice(EMAIL_DOMAINS) + random.choice(DOMAINS)
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


def createSubjects(numberOfSubjects=5):
    faker = Faker()
    BULK_SUBJECT_LIST = [
        Subject(name=faker.pystr_format(), description=faker.paragraph()) for _ in range(numberOfSubjects)
    ]

    Subject.objects.bulk_create(BULK_SUBJECT_LIST)


def createQuiz(creator=None, subject=None, save=True):
    faker = Faker()

    newQuiz = Quiz()
    newQuiz.name = faker.pystr_format()
    newQuiz.description = faker.paragraph()
    newQuiz.subject = subject
    newQuiz.topic = faker.pystr_format()
    newQuiz.quizDuration = faker.random_number(digits=2)
    newQuiz.maxAttempt = faker.random_number(digits=1)
    newQuiz.difficulty = random.choice([Quiz.Difficulty.EASY, Quiz.Difficulty.MEDIUM, Quiz.Difficulty.HARD])
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


def createRandomQuestions(numberOfQuestions=None, save=True):
    if numberOfQuestions is None:
        numberOfQuestions = random.randint(5, 50)

    BULK_QUESTIONS = []

    for _ in range(numberOfQuestions):
        questionType = random.choice([Question.Type.ESSAY, Question.Type.TRUE_OR_FALSE, Question.Type.MULTIPLE_CHOICE])

        if questionType == Question.Type.ESSAY:
            BULK_QUESTIONS.append(createEssayQuestion(False))
        elif questionType == Question.Type.TRUE_OR_FALSE:
            BULK_QUESTIONS.append(createTrueOrFalseQuestion(False))
        elif questionType == Question.Type.MULTIPLE_CHOICE:
            BULK_QUESTIONS.append(createMultipleChoiceQuestionAndAnswers(False))

    return Question.objects.bulk_create(BULK_QUESTIONS) if save else BULK_QUESTIONS


def createEssayQuestion(save=True):
    faker = Faker()
    question = Question(
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


def createTrueOrFalseQuestion(save=True):
    faker = Faker()
    question = Question(
        figure=None,
        content=faker.paragraph(),
        explanation=faker.paragraph(),
        mark=faker.random_number(digits=2),
        questionType=Question.Type.TRUE_OR_FALSE,
        trueOrFalse=random.choice([Question.TrueOrFalse.TRUE, Question.TrueOrFalse.FALSE])
    )

    if save:
        question.save()
    return question


def createMultipleChoiceQuestionAndAnswers(save=True):
    faker = Faker()
    choiceType = random.choice([Question.ChoiceType.SINGLE, Question.ChoiceType.MULTIPLE])
    choices = [
        {
            'id': uuid.uuid4().hex,
            'content': faker.paragraph(),
            'isChecked': False if choiceType == Question.ChoiceType.SINGLE else random.choice(BOOLEAN)
        } for _ in range(random.randint(2, 10))
    ]

    if choiceType == Question.ChoiceType.SINGLE:
        random.choice(choices)['isChecked'] = True

    question = Question(
        figure=None,
        content=faker.paragraph(),
        explanation=faker.paragraph(),
        mark=faker.random_number(digits=2),
        questionType=Question.Type.MULTIPLE_CHOICE,
        choiceOrder=random.choice([Question.ChoiceOrder.SEQUENTIAL, Question.ChoiceOrder.RANDOM, Question.ChoiceOrder.NONE]),
        choiceType=choiceType,
        choices={'choices': choices}
    )

    if save:
        question.save()
    return question
