import datetime
import random

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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


class Question(BaseModel):
    figure = models.ImageField(blank=True, null=True, upload_to='uploads/%Y/%m/%d')
    content = models.TextField()
    explanation = models.TextField(max_length=2048, blank=True, null=True)
    mark = models.SmallIntegerField(blank=True, null=True, default=1)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def getInstanceType(self):
        return self.__class__.__name__


class EssayQuestion(BaseModel):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, primary_key=True, related_name='essayQuestion')
    answer = models.TextField()

    class Meta:
        verbose_name = 'EssayQuestion'
        verbose_name_plural = 'EssayQuestions'


class MultipleChoiceQuestion(BaseModel):
    class Order(models.TextChoices):
        SEQUENTIAL = 'SEQUENTIAL', _('Sequential')
        RANDOM = 'RANDOM', _('Random')
        NONE = 'NONE', _('None')

    question = models.OneToOneField(Question, on_delete=models.CASCADE, primary_key=True, related_name='multipleChoiceQuestion')
    answerOrder = models.CharField(max_length=30, choices=Order.choices, default=Order.RANDOM)
    choices = models.JSONField()

    def orderAnswers(self, queryset):
        if self.answerOrder == self.Order.SEQUENTIAL:
            return queryset.order_by('id')
        if self.answerOrder == self.Order.RANDOM:
            return queryset.order_by('?')
        if self.answerOrder == self.Order.NONE:
            return queryset.order_by()
        return queryset

    class Meta:
        verbose_name = 'MultipleChoiceQuestion'
        verbose_name_plural = 'MultipleChoiceQuestions'


class TrueOrFalseQuestion(BaseModel):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, primary_key=True, related_name='trueOrFalseQuestion')
    isCorrect = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'TrueOrFalseQuestion'
        verbose_name_plural = 'TrueOrFalseQuestions'


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
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjectQuizzes')
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
        return f"{self.id} - {self.name}"

    def getQuestions(self, shuffleQuestions=False):
        questionList = self.questions.all()
        if shuffleQuestions:
            questionList = questionList.order_by('?')
        return questionList

    def getUrl(self):
        return reverse('quiz:quiz-detail-view', kwargs={'quizId': self.id})


class Response(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    isCorrect = models.BooleanField(default=False)
    mark = models.DecimalField(blank=True, null=True, default=None, max_digits=4, decimal_places=2)

    class Meta:
        verbose_name = 'Response'
        verbose_name_plural = 'Response'


class EssayResponse(BaseModel):
    response = models.OneToOneField(Response, on_delete=models.CASCADE, primary_key=True, related_name='essayResponse')
    answer = models.TextField()

    class Meta:
        verbose_name = 'EssayResponse'
        verbose_name_plural = 'EssayResponse'


class MultipleChoiceResponse(BaseModel):
    response = models.OneToOneField(Response, on_delete=models.CASCADE, primary_key=True, related_name='multipleChoiceResponse')
    answers = models.JSONField()

    class Meta:
        verbose_name = 'MultipleChoiceResponse'
        verbose_name_plural = 'MultipleChoiceResponse'


class TrueOrFalseResponse(BaseModel):
    response = models.OneToOneField(Response, on_delete=models.CASCADE, primary_key=True, related_name='trueOrFalseResponse')
    trueSelected = models.BooleanField(blank=True, null=True)

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

    class Mode(models.TextChoices):
        EDIT = 'EDIT', _('Edit')
        MARK = 'MARK', _('Mark')
        VIEW = 'VIEW', _('View')

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NOT_ATTEMPTED)
    responses = models.ManyToManyField(Response, blank=True, related_name='quizAttemptResponses')

    class Meta:
        verbose_name = 'QuizAttempt'
        verbose_name_plural = 'QuizAttempts'

    def getAttemptUrl(self):
        return reverse('quiz:quiz-attempt-view', kwargs={'attemptId': self.id})

    def getAttemptResultUrl(self):
        return reverse('quiz:quiz-attempt-result-view', kwargs={'attemptId': self.id})

    def getQuizEndTime(self, uiFormat=True):
        time = (self.createdDttm + datetime.timedelta(minutes=self.quiz.quizDuration))
        return time.strftime('%b %d, %Y %H:%M:%S') if uiFormat else time

    def hasQuizEnded(self):
        return timezone.now() >= self.getQuizEndTime(False) or self.status in self.getViewStatues()

    def getViewStatues(self):
        return [self.Status.SUBMITTED, self.Status.IN_REVIEW, self.Status.MARKED]

    def getEditStatues(self):
        return [self.Status.NOT_ATTEMPTED, self.Status.IN_PROGRESS]

    def hasViewPermission(self, user):
        if self.user == user:
            return True

        if self.quiz.creator == user and self.status in self.getViewStatues():
            return True

        return False

    def getPermissionMode(self, user):
        if self.user == user and not self.hasQuizEnded() and self.status in self.getEditStatues():
            mode = self.Mode.EDIT
        elif self.quiz.creator == user and self.hasQuizEnded() and self.status != self.Status.MARKED:
            mode = self.Mode.MARK
        elif self.user == user and self.hasQuizEnded() and self.status in self.getViewStatues():
            mode = self.Mode.VIEW
        else:
            raise NotImplementedError('Cannot find a permission mode for quiz attempt: ', self.id)
        return mode


class Result(BaseModel):
    quizAttempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    timeSpent = models.BigIntegerField()
    numberOfCorrectAnswers = models.PositiveSmallIntegerField()
    numberOfPartialAnswers = models.PositiveSmallIntegerField()
    numberOfWrongAnswers = models.PositiveSmallIntegerField()
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=PERCENTAGE_VALIDATOR)

    class Meta:
        verbose_name = 'Result'
        verbose_name_plural = 'Results'

    def getTimeSpent(self):
        return str(datetime.timedelta(seconds=self.timeSpent))

    def hasViewPermission(self, user):
        return self.quizAttempt.user == user or self.quizAttempt.quiz.creator == user
