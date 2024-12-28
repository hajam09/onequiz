import copy
import datetime
import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


def generateModelUrl():
    return f'{uuid.uuid4().hex[:9]}'


class BaseModel(models.Model):
    createdDttm = models.DateTimeField(default=timezone.now)
    modifiedDttm = models.DateTimeField(auto_now=True)
    reference = models.CharField(max_length=1024, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        abstract = True


class Subject(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx-subject-name')
        ]
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'


class Question(BaseModel):
    class Type(models.TextChoices):
        ESSAY = 'ESSAY', _('Essay')
        MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', _('Multiple Choice')
        TRUE_OR_FALSE = 'TRUE_OR_FALSE', _('True or False')
        NONE = 'NONE', _('None')

    class ChoiceOrder(models.TextChoices):
        SEQUENTIAL = 'SEQUENTIAL', _('Sequential')
        RANDOM = 'RANDOM', _('Random')
        NONE = 'NONE', _('None')

    class ChoiceType(models.TextChoices):
        SINGLE = 'SINGLE', _('Single - Allows single choice to be selected')
        MULTIPLE = 'MULTIPLE', _('Multiple - Allows multiple choices to be selected')

    class TrueOrFalse(models.TextChoices):
        TRUE = 'TRUE', _('True')
        FALSE = 'FALSE', _('False')

    url = models.CharField(max_length=10, unique=True, editable=False, default=generateModelUrl)
    figure = models.ImageField(blank=True, null=True, upload_to='uploads/%Y/%m/%d')
    content = models.TextField()
    explanation = models.TextField(max_length=2048, blank=True, null=True)
    mark = models.SmallIntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0)])
    questionType = models.CharField(max_length=32, choices=Type.choices, default=Type.NONE)

    # fields specific to essay
    answer = models.TextField(blank=True, null=True)

    # fields specific to multiple choice
    choiceOrder = models.CharField(max_length=32, choices=ChoiceOrder.choices, default=ChoiceOrder.RANDOM)
    choiceType = models.CharField(max_length=32, choices=ChoiceType.choices, default=ChoiceType.SINGLE)
    choices = models.JSONField(blank=True, null=True)

    # fields specific to true or false
    trueOrFalse = models.CharField(max_length=8, blank=True, null=True, choices=TrueOrFalse.choices)
    # todo: refactor old usage of trueSelected

    class Meta:
        indexes = [
            models.Index(fields=['url'], name='idx-question-url')
        ]
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def orderAnswers(self, queryset):
        if self.questionType == self.Type.NONE:
            raise ValueError('Question type cannot be NONE')

        if self.questionType != self.Type.MULTIPLE_CHOICE:
            return queryset

        if self.choiceOrder == self.ChoiceOrder.SEQUENTIAL:
            return queryset.order_by('id')
        if self.choiceOrder == self.ChoiceOrder.RANDOM:
            return queryset.order_by('?')
        if self.choiceOrder == self.ChoiceOrder.NONE:
            return queryset.order_by()
        return queryset

    def cloneAndCleanChoices(self):
        clonedChoices = copy.deepcopy(self.choices)
        for choice in clonedChoices.get('choices'):
            choice['isChecked'] = False
        return clonedChoices


class Response(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    isCorrect = models.BooleanField(blank=True, null=True, default=None)
    mark = models.DecimalField(blank=True, null=True, default=None, max_digits=4, decimal_places=2)

    # fields specific to essay
    answer = models.TextField(blank=True, null=True)

    # fields specific to multiple choice
    choices = models.JSONField(blank=True, null=True)

    # fields specific to true or false
    trueOrFalse = models.CharField(max_length=8, blank=True, null=True, choices=Question.TrueOrFalse.choices)

    def save(self, *args, **kwargs):
        if self.question.questionType == Question.Type.MULTIPLE_CHOICE and self.id is None:
            self.choices = self.question.cloneAndCleanChoices()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['question'], name='idx-response-question')
        ]
        verbose_name = 'Response'
        verbose_name_plural = 'Responses'

    class ModelManager(models.Manager):
        def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
            for obj in objs:
                if obj.question.questionType == Question.Type.MULTIPLE_CHOICE and obj.id is None:
                    obj.choices = obj.question.cloneAndCleanChoices()
            return super().bulk_create(objs, batch_size, ignore_conflicts)

    objects = ModelManager()


class Quiz(BaseModel):
    class Difficulty(models.TextChoices):
        EASY = 'EASY', _('Easy')
        MEDIUM = 'MEDIUM', _('Medium')
        HARD = 'HARD', _('Hard')

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=10, unique=True, editable=False, default=generateModelUrl)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.CharField(max_length=255, blank=True, null=True)
    quizDuration = models.IntegerField()
    maxAttempt = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    passMark = models.SmallIntegerField(blank=True, default=0, validators=[MaxValueValidator(100)])
    successText = models.TextField(blank=True, null=True)
    failText = models.TextField(blank=True, null=True)
    questions = models.ManyToManyField(Question, blank=True, related_name='quizQuestions')

    inRandomOrder = models.BooleanField(default=False)
    answerAtEnd = models.BooleanField(default=False)
    isExamPaper = models.BooleanField(default=False)
    isDraft = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizCreator')

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx-quiz-name'),
            models.Index(fields=['url'], name='idx-quiz-url'),
            models.Index(fields=['subject'], name='idx-quiz-subject'),
            models.Index(fields=['topic'], name='idx-quiz-topic')
        ]

    def __str__(self):
        return f'{self.id} - {self.name}'

    def getQuestions(self, shuffleQuestions=False):
        questionList = self.questions.all()
        if shuffleQuestions:
            questionList = questionList.order_by('?')
        return questionList

    def getUrl(self):
        return reverse('core:quiz-update-view', kwargs={'url': self.url})


class QuizAttempt(BaseModel):
    class Status(models.TextChoices):
        NOT_ATTEMPTED = 'NOT_ATTEMPTED', _('Not Attempted')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        SUBMITTED = 'SUBMITTED', _('Submitted')
        IN_REVIEW = 'IN_REVIEW', _('In Review')
        MARKED = 'MARKED', _('Marked')

    class Mode(models.TextChoices):
        EDIT = 'EDIT', _('Edit')
        MARK = 'MARK', _('Mark')
        VIEW = 'VIEW', _('View')

    url = models.CharField(max_length=10, unique=True, editable=False, default=generateModelUrl)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quizAttemptQuiz')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizAttemptUser')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NOT_ATTEMPTED)
    responses = models.ManyToManyField(Response, blank=True, related_name='quizAttemptResponses')

    class Meta:
        indexes = [
            models.Index(fields=['url'], name='idx-quiz-attempt-url'),
            models.Index(fields=['quiz'], name='idx-quiz-attempt-quiz'),
            models.Index(fields=['user'], name='idx-quiz-attempt-user')
        ]
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'

    def getAttemptUrl(self):
        return reverse('core:quiz-attempt-view-v3', kwargs={'url': self.url})

    def getAttemptResultUrl(self):
        return reverse('core:quiz-attempt-result-view', kwargs={'url': self.url})

    def getQuizEndTime(self, uiFormat=True):
        endTime = (self.createdDttm + datetime.timedelta(minutes=self.quiz.quizDuration))
        return endTime.strftime('%b %d, %Y %H:%M:%S') if uiFormat else endTime

    def hasQuizEnded(self):
        return timezone.now() >= self.getQuizEndTime(False) or self.status in self.getViewStatues()

    def getViewStatues(self):
        return [self.Status.SUBMITTED, self.Status.IN_REVIEW, self.Status.MARKED]

    def getEditStatues(self):
        return [self.Status.NOT_ATTEMPTED, self.Status.IN_PROGRESS]

    def getSecondsLeft(self):
        return (self.getQuizEndTime(False) - timezone.now()).total_seconds()

    def hasViewPermission(self, user):
        if self.user == user:
            return True

        if self.quiz.creator == user and self.status in self.getViewStatues():
            return True

        return False

    def getPermissionMode(self, user):
        if self.user == user and not self.hasQuizEnded() and self.status in self.getEditStatues():
            mode = self.Mode.EDIT
        elif self.quiz.creator == user and self.hasQuizEnded() and self.status in self.getViewStatues():
            mode = self.Mode.MARK
        elif self.user == user and self.hasQuizEnded() and self.status in self.getViewStatues():
            mode = self.Mode.VIEW
        else:
            raise NotImplementedError(f'Cannot find a permission mode for quiz attempt: {self.id}')
        return mode

    def getResponses(self, shuffle=False):
        responsesList = self.responses.all()
        if shuffle:
            responsesList = responsesList.order_by('?')
        return responsesList


class Result(BaseModel):
    quizAttempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    timeSpent = models.BigIntegerField()
    numberOfCorrectAnswers = models.PositiveSmallIntegerField()
    numberOfPartialAnswers = models.PositiveSmallIntegerField()
    numberOfWrongAnswers = models.PositiveSmallIntegerField()
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=PERCENTAGE_VALIDATOR)

    class Meta:
        indexes = [
            models.Index(fields=['quizAttempt'], name='idx-result-quizAttempt')
        ]
        verbose_name = 'Result'
        verbose_name_plural = 'Results'

    def getTimeSpent(self):
        return str(datetime.timedelta(seconds=self.timeSpent))

    def hasViewPermission(self, user):
        return self.quizAttempt.user == user or self.quizAttempt.quiz.creator == user

    def save(self, *args, **kwargs):
        if not self.timeSpent and self.quizAttempt:
            self.timeSpent = (timezone.now() - self.quizAttempt.createdDttm).seconds
        super(Result, self).save(*args, **kwargs)
