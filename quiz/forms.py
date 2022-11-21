import itertools
import re
import uuid

from django import forms
from django.db import transaction
from django.db.models import Q

from onequiz.operations import generalOperations
from quiz.models import Quiz, Subject, Topic, TrueOrFalseQuestion, EssayQuestion, MultipleChoiceQuestion, Answer


class QuestionForm(forms.Form):
    figure = forms.ImageField(
        label='Figure (Optional)',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    content = forms.CharField(
        label='Content (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    explanation = forms.CharField(
        label='Explanation (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    mark = forms.IntegerField(
        label='Mark',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(QuestionForm, self).__init__(*args, **kwargs)

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        explanation = self.cleaned_data.get('explanation')
        mark = self.cleaned_data.get('mark')

        if not figure and not content:
            self.errors['figure'] = self.error_class([f'Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class([f'Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class([f'Mark cannot be a negative number.'])

        return self.cleaned_data

    def save(self):
        raise NotImplementedError("Please implement save() method")

    def update(self):
        raise NotImplementedError("Please implement update() method")


class QuizForm(forms.Form):
    name = forms.CharField(
        label='Quiz Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
            }
        ),
    )
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    link = forms.CharField(
        label='Quiz link',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
            }
        ),
    )
    subject = forms.MultipleChoiceField(
        label='Subject',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    topic = forms.MultipleChoiceField(
        label='Topic',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    quizDuration = forms.IntegerField(
        label='Quiz Duration (Minutes)',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    maxAttempt = forms.IntegerField(
        label='Quiz Max Attempt',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    difficulty = forms.MultipleChoiceField(
        label='Quiz Difficulty',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    passMark = forms.DecimalField(
        label='Quiz Pass Mark',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    successText = forms.CharField(
        label='Text to display when passed',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
            }
        ),
    )
    failText = forms.CharField(
        label='Text to display when failed',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
            }
        ),
    )
    inRandomOrder = forms.BooleanField(
        label='Questions in random order?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    answerAtEnd = forms.BooleanField(
        label='Show answers at the end?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    isExamPaper = forms.BooleanField(
        label='Exam paper type?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    isDraft = forms.BooleanField(
        label='Is draft?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(QuizForm, self).__init__(*args, **kwargs)

        SUBJECT_CHOICES = [(subject.id, subject.name) for subject in Subject.objects.all()]
        SUBJECT_CHOICES.insert(0, (0, '-- Select a value --'))
        INITIAL_TOPIC_CHOICES = [(0, '-- Select a subject first --')]
        DIFFICULTY_CHOICES = [
            (Quiz.Difficulty.EASY, Quiz.Difficulty.EASY.label),
            (Quiz.Difficulty.MEDIUM, Quiz.Difficulty.MEDIUM.label),
            (Quiz.Difficulty.HARD, Quiz.Difficulty.HARD.label),
        ]

        self.base_fields['difficulty'].choices = DIFFICULTY_CHOICES
        self.base_fields['subject'].choices = SUBJECT_CHOICES
        self.base_fields['topic'].choices = INITIAL_TOPIC_CHOICES

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if Quiz.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError(f'Quiz already exists with name: {name}')

        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')

        if not description:
            raise forms.ValidationError(f'Description should not be empty.')

        return description

    def clean_link(self):
        link = generalOperations.parseStringToUrl(self.cleaned_data.get('link'))

        if Quiz.objects.filter(url__exact=link).exists():
            raise forms.ValidationError(f'Quiz already exists with link: {link}')

        return link

    def clean_subject(self):
        subject = self.data.get('subject')

        if not Subject.objects.filter(id=subject).exists():
            raise forms.ValidationError(f'There\'s an error with the selected subject.')

        return subject

    def clean_topic(self):
        topic = self.data.get('topic')

        if topic == '0':
            raise forms.ValidationError(f'Topic is empty.')
        elif not Topic.objects.filter(id=topic).exists():
            raise forms.ValidationError(f'There\'s an error with the selected topic.')

        return topic

    def clean_quizDuration(self):
        quizDuration = int(self.data.get('quizDuration'))

        if quizDuration < 0:
            raise forms.ValidationError(f'Quiz Durations should be greater than 0.')

        return quizDuration

    def clean_maxAttempt(self):
        maxAttempt = int(self.data.get('maxAttempt'))

        if maxAttempt < 0:
            raise forms.ValidationError(f'Quiz Max Attempt should be greater than 0.')

        return maxAttempt

    def clean_difficulty(self):
        difficulty = self.data.get('difficulty')

        if not (
                difficulty == Quiz.Difficulty.EASY or difficulty == Quiz.Difficulty.MEDIUM or difficulty == Quiz.Difficulty.HARD):
            raise forms.ValidationError(
                f'Quiz Difficulty should either be {Quiz.Difficulty.EASY.label} or {Quiz.Difficulty.MEDIUM.label} or {Quiz.Difficulty.HARD.label}'
            )

        return difficulty

    def clean_passMark(self):
        passMark = self.cleaned_data.get('passMark')

        if passMark < 0 or passMark > 100:
            raise forms.ValidationError(f'Pass mark should be between 0 and 100.')

        return passMark

    def clean_successText(self):
        successText = self.cleaned_data.get('successText')

        if not successText:
            raise forms.ValidationError(f'Text to display when passed should not be empty.')

        return successText

    def clean_failText(self):
        failText = self.cleaned_data.get('failText')

        if not failText:
            raise forms.ValidationError(f'Text to display when failed should not be empty.')

        return failText

    def clean_inRandomOrder(self):
        return self.data.get('inRandomOrder') == 'on'

    def clean_answerAtEnd(self):
        return self.data.get('answerAtEnd') == 'on'

    def clean_isExamPaper(self):
        maxAttempt = self.clean_maxAttempt()
        return maxAttempt is not None and int(maxAttempt) == 1 or self.data.get('isExamPaper') == 'on'

    def clean_isDraft(self):
        return self.data.get('isDraft') == 'on'

    def clean(self):
        raise NotImplementedError("Please implement clean() method")

    def save(self):
        raise NotImplementedError("Please implement save() method")

    def update(self):
        raise NotImplementedError("Please implement update() method")


class QuizCreateForm(QuizForm):

    def __init__(self, request, *args, **kwargs):
        super(QuizCreateForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean(self):
        del self.errors['subject']
        del self.errors['topic']
        del self.errors['difficulty']

        self.clean_subject()
        self.clean_topic()
        self.clean_difficulty()

        return self.cleaned_data

    def save(self):
        newQuiz = Quiz()
        newQuiz.name = self.cleaned_data.get('name')
        newQuiz.description = self.cleaned_data.get('description')
        newQuiz.url = self.cleaned_data.get('link')
        newQuiz.topic_id = self.data.get('topic')
        newQuiz.numberOfQuestions = 1
        newQuiz.quizDuration = self.cleaned_data.get('quizDuration')
        newQuiz.maxAttempt = self.cleaned_data.get('maxAttempt')
        newQuiz.difficulty = self.data.get('difficulty')
        newQuiz.passMark = self.cleaned_data.get('passMark')
        newQuiz.successText = self.cleaned_data.get('successText')
        newQuiz.failText = self.cleaned_data.get('failText')
        newQuiz.inRandomOrder = self.cleaned_data.get('inRandomOrder')
        newQuiz.answerAtEnd = self.cleaned_data.get('answerAtEnd')
        newQuiz.isExamPaper = self.cleaned_data.get('isExamPaper')
        newQuiz.isDraft = self.cleaned_data.get('isDraft')
        newQuiz.creator_id = self.request.user.id
        newQuiz.save()
        return newQuiz


class QuizUpdateForm(QuizForm):

    def __init__(self, request, quiz=None, *args, **kwargs):
        super(QuizUpdateForm, self).__init__(*args, **kwargs)
        self.request = request
        self.quiz = quiz

        if self.quiz is None or not isinstance(quiz, Quiz):
            raise Exception('Quiz is none. or is not instance of Quiz object.')

        INITIAL_TOPIC_CHOICES = [
            (topic.id, topic.name) for topic in Topic.objects.filter(subject_id=self.quiz.topic.subject_id)
        ]
        self.base_fields['topic'].choices = INITIAL_TOPIC_CHOICES

        self.initial['name'] = quiz.name
        self.initial['description'] = quiz.description
        self.initial['link'] = quiz.url
        self.initial['subject'] = self.quiz.topic.subject_id
        self.initial['topic'] = self.quiz.topic.id
        self.initial['quizDuration'] = quiz.quizDuration
        self.initial['maxAttempt'] = quiz.maxAttempt
        self.initial['difficulty'] = quiz.difficulty
        self.initial['passMark'] = quiz.passMark
        self.initial['successText'] = quiz.successText
        self.initial['failText'] = quiz.failText
        self.initial['inRandomOrder'] = quiz.inRandomOrder
        self.initial['answerAtEnd'] = quiz.answerAtEnd
        self.initial['isExamPaper'] = quiz.isExamPaper
        self.initial['isDraft'] = quiz.isDraft

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not name:
            raise forms.ValidationError(f'Quiz name field is empty.')

        return name

    def clean_link(self):
        link = generalOperations.parseStringToUrl(self.cleaned_data.get('link'))

        if Quiz.objects.filter(~Q(id=self.quiz.id), Q(url__exact=link)).exists():
            raise forms.ValidationError(f'Quiz already exists with link: {link}')

        return link

    def clean(self):
        del self.errors['subject']
        del self.errors['topic']
        del self.errors['difficulty']

        self.clean_subject()
        self.clean_topic()
        self.clean_difficulty()

        return self.cleaned_data

    def update(self):
        self.quiz.name = self.cleaned_data.get('name')
        self.quiz.description = self.cleaned_data.get('description')
        self.quiz.url = self.cleaned_data.get('link')
        self.quiz.topic_id = self.data.get('topic')
        self.quiz.quizDuration = self.cleaned_data.get('quizDuration')
        self.quiz.maxAttempt = self.cleaned_data.get('maxAttempt')
        self.quiz.difficulty = self.data.get('difficulty')
        self.quiz.passMark = self.cleaned_data.get('passMark')
        self.quiz.successText = self.cleaned_data.get('successText')
        self.quiz.failText = self.cleaned_data.get('failText')
        self.quiz.inRandomOrder = self.cleaned_data.get('inRandomOrder')
        self.quiz.answerAtEnd = self.cleaned_data.get('answerAtEnd')
        self.quiz.isExamPaper = self.cleaned_data.get('isExamPaper')
        self.quiz.isDraft = self.cleaned_data.get('isDraft')
        self.quiz.save()
        return self.quiz


class EssayQuestionCreateForm(forms.Form):
    figure = forms.ImageField(
        label='Figure (Optional)',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    content = forms.CharField(
        label='Content (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    explanation = forms.CharField(
        label='Explanation (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    mark = forms.IntegerField(
        label='Mark',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    answer = forms.CharField(
        label='Answer',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EssayQuestionCreateForm, self).__init__(*args, **kwargs)

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        mark = self.cleaned_data.get('mark')
        answer = self.cleaned_data.get('answer')

        if not figure and not content:
            self.errors['figure'] = self.error_class([f'Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class([f'Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class([f'Mark cannot be a negative number.'])

        if not answer:
            self.errors['answer'] = self.error_class([f'Answer cannot be left empty.'])

        return self.cleaned_data

    def save(self):
        newEssayQuestion = EssayQuestion.objects.create(
            figure=self.cleaned_data.get('figure'),
            content=self.cleaned_data.get('content'),
            explanation=self.cleaned_data.get('explanation'),
            mark=self.cleaned_data.get('mark'),
            answer=self.cleaned_data.get('answer'),
        )
        return newEssayQuestion


class EssayQuestionUpdateForm(forms.Form):
    figure = forms.ImageField(
        label='Figure (Optional)',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    content = forms.CharField(
        label='Content (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    explanation = forms.CharField(
        label='Explanation (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    mark = forms.IntegerField(
        label='Mark',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    answer = forms.CharField(
        label='Answer',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )

    def __init__(self, essayQuestion=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EssayQuestionUpdateForm, self).__init__(*args, **kwargs)
        self.essayQuestion = None

        if essayQuestion is not None:
            self.essayQuestion = essayQuestion
            # self.initial['figure'] = essayQuestion.figure
            self.initial['content'] = essayQuestion.content
            self.initial['explanation'] = essayQuestion.explanation
            self.initial['mark'] = essayQuestion.mark
            self.initial['answer'] = essayQuestion.answer

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        mark = self.cleaned_data.get('mark')
        answer = self.cleaned_data.get('answer')

        if not figure and not content:
            self.errors['figure'] = self.error_class([f'Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class([f'Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class([f'Mark cannot be a negative number.'])

        if not answer:
            self.errors['answer'] = self.error_class([f'Answer cannot be left empty.'])

        return self.cleaned_data

    def update(self):
        if self.essayQuestion is not None:
            self.essayQuestion.figure = self.cleaned_data.get('figure')
            self.essayQuestion.content = self.cleaned_data.get('content')
            self.essayQuestion.explanation = self.cleaned_data.get('explanation')
            self.essayQuestion.mark = self.cleaned_data.get('mark')
            self.essayQuestion.answer = self.cleaned_data.get('answer')
            self.essayQuestion.save()
        return self.essayQuestion


class MultipleChoiceQuestionCreateForm(forms.Form):
    figure = forms.ImageField(
        label='Figure (Optional)',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    content = forms.CharField(
        label='Content (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    explanation = forms.CharField(
        label='Explanation (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    answerOrder = forms.MultipleChoiceField(
        label='Answer Order',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    mark = forms.IntegerField(
        label='Mark',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(MultipleChoiceQuestionCreateForm, self).__init__(*args, **kwargs)

        ANSWER_ORDER_CHOICES = [
            (None, '-- Select a value --'),
            (MultipleChoiceQuestion.Order.SEQUENTIAL, MultipleChoiceQuestion.Order.SEQUENTIAL.label),
            (MultipleChoiceQuestion.Order.RANDOM, MultipleChoiceQuestion.Order.RANDOM.label),
            (MultipleChoiceQuestion.Order.NONE, MultipleChoiceQuestion.Order.NONE.label),
        ]
        # orderNo, enteredAnswer, isChecked
        ANSWER_OPTIONS = [
            (1, '', False),
            (2, '', False)
        ]
        self.initial['initialAnswerOptions'] = ANSWER_OPTIONS
        self.base_fields['answerOrder'].choices = ANSWER_ORDER_CHOICES

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        mark = self.cleaned_data.get('mark')
        answerOrder = self.data.get('answerOrder')

        del self.errors['answerOrder']

        if not figure and not content:
            self.errors['figure'] = self.error_class([f'Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class([f'Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class([f'Mark cannot be a negative number.'])

        if answerOrder is None:
            self.errors['answerOrder'] = self.error_class(['Answer Order is empty.'])

        answerOptionsList = self.data.getlist('answerOptions')
        isAnswerOptionsValid = True
        ANSWER_OPTIONS = []
        for i in range(len(answerOptionsList)):
            orderNo = i + 1
            enteredAnswer = answerOptionsList[i]
            isChecked = self.data.get(f'answerChecked{orderNo}') == 'on'
            ANSWER_OPTIONS.append((orderNo, enteredAnswer, isChecked))

            if not enteredAnswer:
                isAnswerOptionsValid = False

        if not isAnswerOptionsValid:
            self.errors['initialAnswerOptions'] = self.error_class(
                ['One of your answer options is empty or invalid. Please try again.']
            )

        self.initial['initialAnswerOptions'] = ANSWER_OPTIONS
        return self.cleaned_data

    def save(self):
        answerOptionsList = self.data.getlist('answerOptions')
        choices = [
            {
                'id': uuid.uuid4().hex,
                'content': answerOptionsList[i],
                'isCorrect': self.data.get(f'answerChecked{i + 1}') == 'on'
            }
            for i in range(len(answerOptionsList))
        ]

        newMultipleChoiceQuestion = MultipleChoiceQuestion.objects.create(
            figure=self.cleaned_data.get('figure'),
            content=self.cleaned_data.get('content'),
            explanation=self.cleaned_data.get('explanation'),
            mark=self.cleaned_data.get('mark'),
            answerOrder=self.data.get('answerOrder'),
            choices={'choices': choices}
        )
        return newMultipleChoiceQuestion


class MultipleChoiceQuestionUpdateForm(forms.Form):
    figure = forms.ImageField(
        label='Figure (Optional)',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    content = forms.CharField(
        label='Content (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    explanation = forms.CharField(
        label='Explanation (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    answerOrder = forms.MultipleChoiceField(
        label='Answer Order',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    mark = forms.IntegerField(
        label='Mark',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )

    def __init__(self, multipleChoiceQuestion=None, *args, **kwargs):
        # TODO: Refactor this, re do this.
        kwargs.setdefault('label_suffix', '')
        super(MultipleChoiceQuestionUpdateForm, self).__init__(*args, **kwargs)
        self.multipleChoiceQuestion = None

        ANSWER_ORDER_CHOICES = [
            (None, '-- Select a value --'),
            (MultipleChoiceQuestion.Order.SEQUENTIAL, MultipleChoiceQuestion.Order.SEQUENTIAL.label),
            (MultipleChoiceQuestion.Order.RANDOM, MultipleChoiceQuestion.Order.RANDOM.label),
            (MultipleChoiceQuestion.Order.NONE, MultipleChoiceQuestion.Order.NONE.label),
        ]
        # orderNo, enteredAnswer, isChecked
        ANSWER_OPTIONS = [(i, x['content'], x['isCorrect']) for i, x in enumerate(multipleChoiceQuestion.choices['choices'], 1)]

        self.initial['initialAnswerOptions'] = ANSWER_OPTIONS
        self.base_fields['answerOrder'].choices = ANSWER_ORDER_CHOICES

        if multipleChoiceQuestion is not None:
            self.multipleChoiceQuestion = multipleChoiceQuestion
            #     # self.initial['figure'] = essayQuestion.figure
            self.initial['content'] = multipleChoiceQuestion.content
            self.initial['explanation'] = multipleChoiceQuestion.explanation
            self.initial['mark'] = multipleChoiceQuestion.mark
            self.initial['answerOrder'] = multipleChoiceQuestion.answerOrder

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        mark = self.cleaned_data.get('mark')
        answerOrder = self.data.get('answerOrder')

        del self.errors['answerOrder']

        if not figure and not content:
            self.errors['figure'] = self.error_class([f'Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class([f'Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class([f'Mark cannot be a negative number.'])

        # if answerOrder == '0':
        #     self.errors['answerOrder'] = self.error_class(['Answer Order is empty.'])

        answerOptionsList = self.data.getlist('answerOptions')
        isAnswerOptionsValid = True
        ANSWER_OPTIONS = []
        for i in range(len(answerOptionsList)):
            orderNo = i + 1
            enteredAnswer = answerOptionsList[i]
            isChecked = self.data.get(f'answerChecked-{orderNo}') == 'on'
            ANSWER_OPTIONS.append((orderNo, enteredAnswer, isChecked))

            if not enteredAnswer:
                isAnswerOptionsValid = False

        if not isAnswerOptionsValid:
            self.errors['initialAnswerOptions'] = self.error_class(
                ['One of your answer options is empty or invalid. Please try again.']
            )

        self.initial['initialAnswerOptions'] = ANSWER_OPTIONS
        return self.cleaned_data

    def update(self):
        # self.multipleChoiceQuestion.figure = self.cleaned_data.get('figure')
        self.multipleChoiceQuestion.content = self.cleaned_data.get('content')
        self.multipleChoiceQuestion.explanation = self.cleaned_data.get('explanation')
        self.multipleChoiceQuestion.mark = self.cleaned_data.get('mark')
        self.multipleChoiceQuestion.answerOrder = self.data.get('answerOrder')

        newAnswerOptionsList = self.data.getlist('answerOptions')
        oldAnswerOptionsList = self.multipleChoiceQuestion.choices['choices']
        counter = 0
        idsToDelete = []

        for (nl, ol) in itertools.zip_longest(newAnswerOptionsList, oldAnswerOptionsList):
            counter += 1
            isChecked = self.data.get(f'answerChecked-{counter}') == 'on'

            if nl is not None and ol is None:
                # additional answer is added.
                newOption = {
                    'id': uuid.uuid4().hex,
                    'content': nl,
                    'isCorrect': isChecked
                }
                oldAnswerOptionsList.append(newOption)
                continue
            elif nl is None and ol is not None:
                # existing answer is removed.
                idsToDelete.append(ol['id'])

            ol['content'] = nl
            ol['isCorrect'] = isChecked

        self.multipleChoiceQuestion.choices = {
            'choices': [i for i in oldAnswerOptionsList if i['id'] not in idsToDelete]
        }
        self.multipleChoiceQuestion.save()
        return self.multipleChoiceQuestion


class TrueOrFalseQuestionCreateForm(forms.Form):
    figure = forms.ImageField(
        label='Figure (Optional)',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    content = forms.CharField(
        label='Content (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    explanation = forms.CharField(
        label='Explanation (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    mark = forms.IntegerField(
        label='Mark',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    isCorrect = forms.ChoiceField(
        label='Is the answer True or False?',
        choices=[('True', 'True'), ('False', 'False')],
        required=True,
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        )
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(TrueOrFalseQuestionCreateForm, self).__init__(*args, **kwargs)

        # radioName, value, label, isSelected
        IS_CORRECT_CHOICES = [('isCorrect', 'True', 'True', 'False'), ('isCorrect', 'False', 'False', 'False')]
        self.initial['isCorrectChoices'] = IS_CORRECT_CHOICES

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        mark = self.cleaned_data.get('mark')

        if not figure and not content:
            self.errors['figure'] = self.error_class([f'Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class([f'Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class([f'Mark cannot be a negative number.'])

        # radioName, value, label, isSelected
        IS_CORRECT_CHOICES = [('isCorrect', 'True', 'True', 'False'), ('isCorrect', 'False', 'False', 'False')]
        choiceIndexNumberToChange = 0 if self.cleaned_data.get('isCorrect') == 'True' else 1
        tempList = list(IS_CORRECT_CHOICES[choiceIndexNumberToChange])
        tempList[3] = 'True'
        IS_CORRECT_CHOICES[choiceIndexNumberToChange] = tuple(tempList)

        # if self.cleaned_data.get('isCorrect') == 'True':
        #     tempList = list(IS_CORRECT_CHOICES[0])
        #     tempList[3] = 'True'
        #     IS_CORRECT_CHOICES[0] = tuple(tempList)
        # else:
        #     tempList = list(IS_CORRECT_CHOICES[1])
        #     tempList[3] = 'True'
        #     IS_CORRECT_CHOICES[1] = tuple(tempList)

        self.initial['isCorrectChoices'] = IS_CORRECT_CHOICES
        return self.cleaned_data

    def save(self):
        newTrueOrFalseQuestion = TrueOrFalseQuestion.objects.create(
            figure=self.cleaned_data.get('figure'),
            content=self.cleaned_data.get('content'),
            explanation=self.cleaned_data.get('explanation'),
            mark=self.cleaned_data.get('mark'),
            isCorrect=eval(self.cleaned_data.get('isCorrect')),
        )
        return newTrueOrFalseQuestion


class TrueOrFalseQuestionUpdateForm(forms.Form):
    figure = forms.ImageField(
        label='Figure (Optional)',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    content = forms.CharField(
        label='Content (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    explanation = forms.CharField(
        label='Explanation (Optional)',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )
    mark = forms.IntegerField(
        label='Mark',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    isCorrect = forms.ChoiceField(
        label='Is the answer True or False?',
        choices=[('True', 'True'), ('False', 'False')],
        initial='True',
        required=True,
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        )
    )

    def __init__(self, trueOrFalseQuestion=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(TrueOrFalseQuestionUpdateForm, self).__init__(*args, **kwargs)
        self.trueOrFalseQuestion = trueOrFalseQuestion

        # radioName, value, label, isSelected
        IS_CORRECT_CHOICES = [('isCorrect', 'True', 'True', 'False'), ('isCorrect', 'False', 'False', 'False')]

        if self.trueOrFalseQuestion is not None:
            # self.initial['figure'] = self.trueOrFalseQuestion.figure
            self.initial['content'] = self.trueOrFalseQuestion.content
            self.initial['explanation'] = self.trueOrFalseQuestion.explanation
            self.initial['mark'] = self.trueOrFalseQuestion.mark

            choiceIndexNumberToUpdate = 0 if self.trueOrFalseQuestion.isCorrect else 1
            tempList = list(IS_CORRECT_CHOICES[choiceIndexNumberToUpdate])
            tempList[3] = 'True'
            IS_CORRECT_CHOICES[choiceIndexNumberToUpdate] = tuple(tempList)
            self.initial['isCorrectChoices'] = IS_CORRECT_CHOICES

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        mark = self.cleaned_data.get('mark')

        if not figure and not content:
            self.errors['figure'] = self.error_class([f'Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class([f'Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class([f'Mark cannot be a negative number.'])

        # radioName, value, label, isSelected
        IS_CORRECT_CHOICES = [('isCorrect', 'True', 'True', 'False'), ('isCorrect', 'False', 'False', 'False')]
        choiceIndexNumberToChange = 0 if self.cleaned_data.get('isCorrect') == 'True' else 1
        tempList = list(IS_CORRECT_CHOICES[choiceIndexNumberToChange])
        tempList[3] = 'True'
        IS_CORRECT_CHOICES[choiceIndexNumberToChange] = tuple(tempList)
        self.initial['isCorrectChoices'] = IS_CORRECT_CHOICES

        return self.cleaned_data

    def update(self):
        self.trueOrFalseQuestion.figure = self.cleaned_data.get('figure')
        self.trueOrFalseQuestion.content = self.cleaned_data.get('content')
        self.trueOrFalseQuestion.explanation = self.cleaned_data.get('explanation')
        self.trueOrFalseQuestion.mark = self.cleaned_data.get('mark')
        self.trueOrFalseQuestion.isCorrect = eval(self.cleaned_data.get('isCorrect'))
        self.trueOrFalseQuestion.save()
        return self.trueOrFalseQuestion
