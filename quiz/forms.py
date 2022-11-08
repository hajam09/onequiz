import re

from django import forms
from django.core.exceptions import ValidationError

from quiz.models import Quiz, Subject, Topic


class QuizCreationForm(forms.Form):
    name = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
                'placeholder': 'Quiz name',

            }
        ),
    )
    description = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'placeholder': 'Description',
                'rows': 5,
            }
        )
    )
    link = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
                'placeholder': 'Quiz link',
            }
        ),
    )
    subject = forms.MultipleChoiceField(
        label='',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    topic = forms.MultipleChoiceField(
        label='',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    quizDuration = forms.IntegerField(
        label='',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Quiz duration',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    maxAttempt = forms.IntegerField(
        label='',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Quiz max attempt',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    difficulty = forms.MultipleChoiceField(
        label='',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    passMark = forms.DecimalField(
        label='',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Pass mark',
                'style': 'width: 100%',
                'required': 'required',
            }
        ),
    )
    successText = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
                'placeholder': 'Success text',
            }
        ),
    )
    failText = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
                'placeholder': 'Fail text',
            }
        ),
    )
    inRandomOrder = forms.BooleanField(
        label='Questions in random order?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'style': 'height: 1.25rem; width: 1.25rem',
            }
        ),
    )
    answerAtEnd = forms.BooleanField(
        label='Show answers at the end?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'style': 'height: 1.25rem; width: 1.25rem',
            }
        ),
    )
    isExamPaper = forms.BooleanField(
        label='Exam paper type?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'style': 'height: 1.25rem; width: 1.25rem',
            }
        ),
    )
    isDraft = forms.BooleanField(
        label='Is draft?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'style': 'height: 1.25rem; width: 1.25rem',
            }
        ),
    )

    def __init__(self, request, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(QuizCreationForm, self).__init__(*args, **kwargs)
        self.request = request

        SUBJECT_CHOICES = [
            (subject.id, subject.name) for subject in Subject.objects.all()
        ]

        selectedSubjectId = self.data.get('subject') or SUBJECT_CHOICES[0][0]

        INITIAL_TOPIC_CHOICES = [
            (topic.id, topic.name) for topic in Topic.objects.filter(subject_id=selectedSubjectId)
        ]

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
        description = self.cleaned_data.get('description')
        link = re.sub('\s+', '-', self.cleaned_data.get('link')).lower()
        link = ''.join(letter for letter in link if letter.isalnum() or letter == '-')
        subject = self.data.get('subject')
        topic = self.data.get('topic')
        quizDuration = self.cleaned_data.get('quizDuration')
        maxAttempt = self.cleaned_data.get('maxAttempt')
        difficulty = self.data.get('difficulty')
        passMark = self.cleaned_data.get('passMark')
        successText = self.cleaned_data.get('successText')
        failText = self.cleaned_data.get('failText')
        inRandomOrder = self.cleaned_data.get('inRandomOrder')
        answerAtEnd = self.cleaned_data.get('answerAtEnd')
        isExamPaper = self.cleaned_data.get('isExamPaper')
        isDraft = self.cleaned_data.get('isDraft')

        del self.errors['difficulty']
        del self.errors['subject']
        del self.errors['topic']

        INITIAL_TOPIC_CHOICES = [
            (topic.id, topic.name) for topic in Topic.objects.filter(subject_id=subject)
        ]
        self.base_fields['topic'].choices = INITIAL_TOPIC_CHOICES

        validationErrorList = []

        if Quiz.objects.filter(name__iexact=name).exists():
            validationErrorList.append(
                ValidationError({'name': f'Quiz already exists with name: {name}'})
            )
        if Quiz.objects.filter(url__exact=link).exists():
            validationErrorList.append(
                ValidationError({'name': f'Quiz already exists with link: {link}'})
            )

        if passMark > 100:
            raise ValidationError({'passMark': 'Pass mark is above 100.'})

        if len(validationErrorList) > 0:
            raise ValidationError(validationErrorList)

        newQuiz = Quiz()
        newQuiz.name = name
        newQuiz.description = description
        newQuiz.url = link
        newQuiz.topic_id = topic
        newQuiz.numberOfQuestions = 1
        newQuiz.quizDuration = quizDuration
        newQuiz.maxAttempt = maxAttempt
        newQuiz.difficulty = difficulty
        newQuiz.passMark = passMark
        newQuiz.successText = successText
        newQuiz.failText = failText
        newQuiz.inRandomOrder = inRandomOrder
        newQuiz.answerAtEnd = answerAtEnd
        newQuiz.isExamPaper = isExamPaper
        newQuiz.isDraft = isDraft
        newQuiz.creator_id = self.request.user.id

        if maxAttempt == 1:
            self.isExamPaper = True

        newQuiz.save()

        return self.cleaned_data
