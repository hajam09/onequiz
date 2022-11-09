import re

from django import forms
from django.db import transaction

from quiz.models import Quiz, Subject, Topic, TrueOfFalseQuestion, EssayQuestion, MultipleChoiceQuestion, Answer


class QuizCreationForm(forms.Form):
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

    def __init__(self, request, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(QuizCreationForm, self).__init__(*args, **kwargs)
        self.request = request

        SUBJECT_CHOICES = [(0, '-- Select a value --')]
        for subject in Subject.objects.all():
            SUBJECT_CHOICES.append((subject.id, subject.name))

        # selectedSubjectId = self.data.get('subject') or SUBJECT_CHOICES[0][0]
        # INITIAL_TOPIC_CHOICES = [
        #     (topic.id, topic.name) for topic in Topic.objects.filter(subject_id=selectedSubjectId)
        # ]

        INITIAL_TOPIC_CHOICES = [(0, '-- Select a subject first --')]

        DIFFICULTY_CHOICES = [
            (Quiz.Difficulty.EASY, Quiz.Difficulty.EASY.label),
            (Quiz.Difficulty.MEDIUM, Quiz.Difficulty.MEDIUM.label),
            (Quiz.Difficulty.HARD, Quiz.Difficulty.HARD.label),
        ]
        self.base_fields['difficulty'].choices = DIFFICULTY_CHOICES
        self.base_fields['subject'].choices = SUBJECT_CHOICES
        self.base_fields['topic'].choices = INITIAL_TOPIC_CHOICES

    def clean(self):
        name = self.cleaned_data.get('name')
        link = re.sub('\s+', '-', self.cleaned_data.get('link')).lower()
        link = ''.join(letter for letter in link if letter.isalnum() or letter == '-')
        subject = self.data.get('subject')
        topic = self.data.get('topic')
        maxAttempt = self.cleaned_data.get('maxAttempt')
        passMark = self.cleaned_data.get('passMark')

        del self.errors['difficulty']
        del self.errors['subject']
        del self.errors['topic']

        INITIAL_TOPIC_CHOICES = [
            (topic.id, topic.name) for topic in Topic.objects.filter(subject_id=subject)
        ]
        self.base_fields['topic'].choices = INITIAL_TOPIC_CHOICES

        if Quiz.objects.filter(name__iexact=name).exists():
            self.errors['name'] = self.error_class([f'Quiz already exists with name: {name}'])

        if Quiz.objects.filter(url__exact=link).exists():
            self.errors['link'] = self.error_class([f'Quiz already exists with link: {link}'])

        if passMark > 100:
            self.errors['passMark'] = self.error_class(['Pass mark is above 100.'])

        if topic == '0':
            self.errors['topic'] = self.error_class(['Topic is empty.'])

        if maxAttempt == 1:
            self.isExamPaper = True

        return self.cleaned_data

    def save(self):
        link = re.sub('\s+', '-', self.cleaned_data.get('link')).lower()
        link = ''.join(letter for letter in link if letter.isalnum() or letter == '-')

        newQuiz = Quiz()
        newQuiz.name = self.cleaned_data.get('name')
        newQuiz.description = self.cleaned_data.get('description')
        newQuiz.url = link
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


class EssayQuestionForm(forms.Form):
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
        super(EssayQuestionForm, self).__init__(*args, **kwargs)

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


class MultipleChoiceQuestionForm(forms.Form):
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
        super(MultipleChoiceQuestionForm, self).__init__(*args, **kwargs)

        ANSWER_ORDER_CHOICES = [
            (0, '-- Select a value --'),
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

        if answerOrder == '0':
            self.errors['answerOrder'] = self.error_class(['Answer Order is empty.'])

        answerValueList = self.data.getlist('answerValue')
        ANSWER_OPTIONS = []
        for i in range(len(answerValueList)):
            orderNo = i + 1
            enteredAnswer = answerValueList[i]
            isChecked = self.data.get(f'answerChecked{orderNo}') == 'on'
            ANSWER_OPTIONS.append((orderNo, enteredAnswer, isChecked))

        self.initial['initialAnswerOptions'] = ANSWER_OPTIONS
        return self.cleaned_data

    def save(self):
        answerValueList = self.data.getlist('answerValue')
        bulkAnswer = []

        with transaction.atomic():
            newMultipleChoiceQuestion = MultipleChoiceQuestion.objects.create(
                figure=self.cleaned_data.get('figure'),
                content=self.cleaned_data.get('content'),
                explanation=self.cleaned_data.get('explanation'),
                mark=self.cleaned_data.get('mark'),
                answerOrder=self.data.get('answerOrder')
            )

            for i in range(len(answerValueList)):
                enteredAnswer = answerValueList[i]
                isChecked = self.data.get(f'answerChecked{i + 1}') == 'on'
                bulkAnswer.append(
                    Answer(
                        question=newMultipleChoiceQuestion,
                        content=enteredAnswer,
                        isCorrect=isChecked
                    )
                )
            Answer.objects.bulk_create(bulkAnswer)
        return newMultipleChoiceQuestion


class TrueOrFalseQuestionForm(forms.Form):
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
        super(TrueOrFalseQuestionForm, self).__init__(*args, **kwargs)

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        mark = self.cleaned_data.get('mark')

        if not figure and not content:
            self.errors['figure'] = self.error_class([f'Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class([f'Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class([f'Mark cannot be a negative number.'])

        return self.cleaned_data

    def save(self):
        newTrueOfFalseQuestion = TrueOfFalseQuestion.objects.create(
            figure=self.cleaned_data.get('figure'),
            content=self.cleaned_data.get('content'),
            explanation=self.cleaned_data.get('explanation'),
            mark=self.cleaned_data.get('mark'),
            isCorrect=eval(self.cleaned_data.get('isCorrect')),
        )
        return newTrueOfFalseQuestion
