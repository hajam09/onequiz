import random

from django.conf import settings
from django.contrib.auth.models import User
from faker import Faker

from onequiz.operations import generalOperations
from quiz.models import Subject, Topic, Quiz, EssayQuestion, TrueOrFalseQuestion, MultipleChoiceQuestion, Answer

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


def createSubjectsAndTopics():
    faker = Faker()
    BULK_SUBJECT_LIST = []
    BULK_TOPIC_LIST = []

    for _ in range(5):
        subject = Subject(name=faker.pystr_format(), description=faker.paragraph())
        BULK_SUBJECT_LIST.append(subject)

        for _ in range(10):
            BULK_TOPIC_LIST.append(
                Topic(
                    name=faker.pystr_format(),
                    subject=subject,
                    description=faker.paragraph()
                )
            )

    Subject.objects.bulk_create(BULK_SUBJECT_LIST)
    subjectNameUnique = list(set([i.name for i in BULK_SUBJECT_LIST]))
    subjectList = Subject.objects.filter(name__in=subjectNameUnique)

    topicNameUnique = []

    for subject in subjectList:
        for topic in BULK_TOPIC_LIST:
            if subject.name == topic.subject.name:
                topic.subject = subject

            if topic.name not in topicNameUnique:
                topicNameUnique.append(topic.name)

    Topic.objects.bulk_create(BULK_TOPIC_LIST)
    topicList = Topic.objects.filter(name__in=topicNameUnique)
    return subjectList, topicList


def createQuiz(creator=None, topic=None):
    faker = Faker()

    newQuiz = Quiz()
    newQuiz.name = faker.pystr_format()
    newQuiz.description = faker.paragraph()
    newQuiz.url = generalOperations.parseStringToUrl(faker.paragraph())
    newQuiz.topic = topic
    newQuiz.numberOfQuestions = faker.random_number(digits=2, fix_len=False)
    newQuiz.quizDuration = faker.random_number(digits=2)
    newQuiz.maxAttempt = faker.random_number(digits=1)
    newQuiz.difficulty = random.choice([Quiz.Difficulty.EASY, Quiz.Difficulty.MEDIUM, Quiz.Difficulty.HARD])
    newQuiz.passMark = faker.random_number(digits=2)
    newQuiz.successText = faker.paragraph()
    newQuiz.failText = faker.paragraph()
    # newQuiz.questions = None
    newQuiz.inRandomOrder = random.choice(BOOLEAN)
    newQuiz.answerAtEnd = random.choice(BOOLEAN)
    newQuiz.isExamPaper = random.choice(BOOLEAN)
    newQuiz.isDraft = random.choice(BOOLEAN)
    newQuiz.creator = creator if creator is not None else createUser()
    newQuiz.save()
    newQuiz.refresh_from_db()
    return newQuiz


def createEssayQuestion():
    faker = Faker()
    newEssayQuestion = EssayQuestion.objects.create(
        figure=None,
        content=faker.paragraph(),
        explanation=faker.paragraph(),
        mark=faker.random_number(digits=2),
        answer=faker.paragraph()
    )
    return newEssayQuestion


def createTrueOrFalseQuestion():
    faker = Faker()
    newTrueOrFalseQuestion = TrueOrFalseQuestion.objects.create(
        figure=None,
        content=faker.paragraph(),
        explanation=faker.paragraph(),
        mark=faker.random_number(digits=2),
        isCorrect=random.choice(BOOLEAN),
    )
    return newTrueOrFalseQuestion


def createMultipleChoiceQuestionAndAnswers(answerOptions=None):
    faker = Faker()
    bulkAnswer = []
    answerOptions = answerOptions or []

    newMultipleChoiceQuestion = MultipleChoiceQuestion.objects.create(
        figure=None,
        content=faker.paragraph(),
        explanation=faker.paragraph(),
        mark=faker.random_number(digits=2)
    )

    for answer in answerOptions:
        bulkAnswer.append(
            Answer(
                question=newMultipleChoiceQuestion,
                content=answer[1],
                isCorrect=answer[2]
            )
        )
    Answer.objects.bulk_create(bulkAnswer)
    return newMultipleChoiceQuestion
