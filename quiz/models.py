import datetime
import random

import jsonfield
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.managers import InheritanceManager

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class BaseModel(models.Model):
    createdDttm = models.DateTimeField(default=timezone.now)
    modifiedDttm = models.DateTimeField(auto_now=True)
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        abstract = True


class Subject(BaseModel):
    # Maths, Science, Geography, ...
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def getSubjectTopics(self):
        return self.subjectTopics.all().order_by('name')


class Topic(BaseModel):
    """
    Within the subject they could be tested in specific topic.
    e.g -> Maths (Algebra, Probability, ...)
    e.g -> Chemistry (Atomic structure, Chemical bonds, ...)
    """
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subjectTopics')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'


class Question(BaseModel):
    figure = models.ImageField(blank=True, null=True, upload_to='uploads/%Y/%m/%d')
    content = models.TextField()
    explanation = models.TextField(max_length=2048, blank=True, null=True)
    mark = models.SmallIntegerField(blank=True, null=True, default=1)

    objects = InheritanceManager()

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'


class EssayQuestion(Question):
    answer = models.TextField()

    def checkIfCorrect(self, guess):
        return False

    def getAnswers(self):
        return False

    def getAnswersList(self):
        return False

    def answerChoiceToString(self, guess):
        return str(guess)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'EssayQuestion'
        verbose_name_plural = 'EssayQuestions'


class MultipleChoiceQuestion(Question):
    class Order(models.TextChoices):
        SEQUENTIAL = 'SEQUENTIAL', _('Sequential')
        RANDOM = 'RANDOM', _('Random')
        NONE = 'NONE', _('None')

    answerOrder = models.CharField(max_length=30, choices=Order.choices, default=Order.RANDOM)
    choices = jsonfield.JSONField()

    def checkIfCorrect(self, pk):
        answer = Answer.objects.get(id=pk)
        return answer.isCorrect

    def orderAnswers(self, queryset):
        if self.answerOrder == self.Order.SEQUENTIAL:
            return queryset.order_by('id')
        if self.answerOrder == self.Order.RANDOM:
            return queryset.order_by('?')
        if self.answerOrder == self.Order.NONE:
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.orderAnswers(Answer.objects.filter(question=self))

    def getAnswers(self):
        return Answer.objects.filter(question=self)

    def getAnswersList(self):
        return [(answer.id, answer.content) for answer in self.orderAnswers(Answer.objects.filter(question=self))]

    def answerChoiceToString(self, guess):
        return Answer.objects.get(id=guess).content

    class Meta:
        verbose_name = 'MultipleChoiceQuestion'
        verbose_name_plural = 'MultipleChoiceQuestions'


class TrueOrFalseQuestion(Question):
    isCorrect = models.BooleanField(default=False)

    def checkIfCorrect(self, guess):
        if guess == "True":
            guessBool = True
        elif guess == "False":
            guessBool = False
        else:
            return False

        return guessBool == self.isCorrect

    def getAnswers(self):
        context = [
            {'correct': self.checkIfCorrect("True"), 'content': 'True'},
            {'correct': self.checkIfCorrect("False"), 'content': 'False'}
        ]
        return context

    def getAnswersList(self):
        return [(True, True), (False, False)]

    def answerChoiceToString(self, guess):
        return str(guess)

    class Meta:
        verbose_name = 'TrueOrFalseQuestion'
        verbose_name_plural = 'TrueOrFalseQuestions'


# TODO: Refactor
class Answer(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    isCorrect = models.BooleanField(default=False)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    # def ifCorrect(self, userAnswer):
    #     stripeText = re.sub(' +', ' ', self.content)
    #     stripeUserAnswer = re.sub(' +', ' ', userAnswer)
    #     return stripeText.casefold() == stripeUserAnswer.casefold()


class Quiz(BaseModel):
    """
    The base of our app
    """

    class Difficulty(models.TextChoices):
        EASY = 'EASY', _('Easy')
        MEDIUM = 'MEDIUM', _('Medium')
        HARD = 'HARD', _('Hard')

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.SlugField(max_length=255, blank=False)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='topicQuizzes')
    numberOfQuestions = models.PositiveIntegerField()
    quizDuration = models.IntegerField()
    maxAttempt = models.PositiveIntegerField(default=False)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    passMark = models.SmallIntegerField(blank=True, default=0, validators=[MaxValueValidator(100)])
    successText = models.TextField(blank=True, null=True)
    failText = models.TextField(blank=True, null=True)
    questions = models.ManyToManyField(Question, blank=True, related_name='quizQuestions')

    inRandomOrder = models.BooleanField(default=False)
    answerAtEnd = models.BooleanField(default=False)
    isExamPaper = models.BooleanField(default=False)
    isDraft = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.name} - {self.topic.name}"

    def getQuestions(self, shuffleQuestions=False):
        questionList = self.questions.all().select_subclasses()
        if shuffleQuestions:
            random.shuffle(questionList)
        return questionList

    def getUrl(self):
        return reverse('quiz:quiz-detail-view', kwargs={'quizId': self.id})

    # @property
    # def getQuestions(self):
    #     questions = list(self.questions.all())
    #     if self.inRandomOrder:
    #         random.shuffle(questions)
    #     return questions

    @property
    def getMaxScore(self):
        return self.getQuestions().count()


# class ProgressManager(models.Manager):
#
#     def newProgress(self, user):
#         newProgress = self.create(user=user, score='')
#         newProgress.save()
#         return newProgress
#
#
# class Progress(BaseModel):
#     """
#        Progress is used to track an individual signed in users score on different
#        quiz's and categories
#        Data stored in csv using the format:
#            category, score, possible, category, score, possible, ...
#     """
#     user = models.OneToOneField(User, on_delete=models.CASCADE)


# class Question(BaseModel):
#     class AnswerType(models.TextChoices):
#         TEXT = 'TEXT', _('Text')  # free text -> answer depends on the user.
#         RADIO_BOX = 'RADIO_BOX', _('Radio box')  # radio box options -> single correct answer from multiple choices.
#         CHECK_BOX = 'CHECK_BOX', _('Check box')  # check box options -> multiple correct answers from multiple choices
#
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
#     figure = models.ImageField(blank=True, null=True, upload_to='uploads/%Y/%m/%d')
#     content = models.TextField()
#     answerType = models.CharField(max_length=64, choices=AnswerType.choices)
#     explanation = models.TextField(max_length=2048, blank=True, null=True)
#
#     objects = InheritanceManager()
#
#     @property
#     def getAnswers(self):
#         return self.answers.all()


# class Answer(BaseModel):
#     content = models.TextField()
#     isCorrect = models.BooleanField(default=False)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
#     marks = models.SmallIntegerField(blank=True, null=True, default=1)

# def ifCorrect(self, userAnswer):
#     stripeText = re.sub(' +', ' ', self.content)
#     stripeUserAnswer = re.sub(' +', ' ', userAnswer)
#     return stripeText.casefold() == stripeUserAnswer.casefold()


class Result(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=PERCENTAGE_VALIDATOR)

    class Meta:
        verbose_name = 'Result'
        verbose_name_plural = 'Results'


class Response(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    isCorrect = models.BooleanField(default=False)
    mark = models.SmallIntegerField(blank=True, null=True, default=0)

    objects = InheritanceManager()

    class Meta:
        verbose_name = 'Response'
        verbose_name_plural = 'Response'


class EssayResponse(Response):
    answer = models.TextField()

    class Meta:
        verbose_name = 'EssayResponse'
        verbose_name_plural = 'EssayResponse'


class MultipleChoiceResponse(Response):
    answers = jsonfield.JSONField()

    class Meta:
        verbose_name = 'MultipleChoiceResponse'
        verbose_name_plural = 'MultipleChoiceResponse'


class TrueOrFalseResponse(Response):
    # TODO: change this to isTrueChecked
    isChecked = models.BooleanField(blank=True, null=True, default=False)

    class Meta:
        verbose_name = 'TrueOrFalseResponse'
        verbose_name_plural = 'TrueOrFalseResponse'


class QuizAttempt(BaseModel):
    class Status(models.TextChoices):
        NOT_ATTEMPTED = 'NOT_ATTEMPTED', _('Non Attempted')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        SUBMITTED = 'SUBMITTED', _('Submitted')
        IN_REVIEW = 'IN_REVIEW', _('In Review')
        MARKED = 'MARKED', _('Marked')

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NOT_ATTEMPTED)
    responses = models.ManyToManyField(Response, blank=True, related_name='quizAttemptResponses')

    class Meta:
        verbose_name = 'QuizAttempt'
        verbose_name_plural = 'QuizAttempts'

    def getQuizEndTime(self, uiFormat=True):
        time = (self.createdDttm + datetime.timedelta(minutes=self.quiz.quizDuration))
        return time.strftime('%b %d, %Y %H:%M:%S') if uiFormat else time
