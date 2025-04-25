from django import forms

from core.models import Quiz, Question
from onequiz.operations import generalOperations


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
    subject = forms.ChoiceField(
        label='Subject',
        choices=[(None, '-- Select a value --')] + Quiz.Subject.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    topic = forms.CharField(
        label='Topic',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
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
                'min': '0',
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
                'min': '0',
            }
        ),
    )
    difficulty = forms.ChoiceField(
        label='Quiz Difficulty',
        choices=[(None, '-- Select a value --')] + Quiz.Difficulty.choices,
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
                'min': '0',
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
    enableAutoMarking = forms.BooleanField(
        label='Enabled auto marking?',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-control',
            }
        ),
        help_text='Note: Auto-marking won\'t apply for quiz with essay questions!'
    )

    def __init__(self, request, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if Quiz.objects.filter(name__iexact=name, creator=self.request.user).exists():
            raise forms.ValidationError(f'Quiz already exists with name: {name}')

        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')

        if not description:
            raise forms.ValidationError('Description should not be empty.')

        return description

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')

        if subject not in Quiz.Subject.values:
            raise forms.ValidationError('Select a subject from the list provided.')

        return subject

    def clean_topic(self):
        topic = self.cleaned_data.get('topic')

        if not topic:
            raise forms.ValidationError('Topic should not be empty.')

        return topic

    def clean_quizDuration(self):
        quizDuration = int(self.cleaned_data.get('quizDuration'))

        if quizDuration < 0:
            raise forms.ValidationError('Quiz Durations should be greater than 0.')

        return quizDuration

    def clean_maxAttempt(self):
        maxAttempt = int(self.cleaned_data.get('maxAttempt', 1))

        if maxAttempt < 0:
            raise forms.ValidationError('Quiz Max Attempt should be greater than 0.')

        return maxAttempt

    def clean_difficulty(self):
        difficulty = self.cleaned_data.get('difficulty')

        if difficulty not in Quiz.Difficulty.values:
            raise forms.ValidationError('Select a difficulty from the list provided.')

        return difficulty

    def clean_passMark(self):
        passMark = self.cleaned_data.get('passMark')

        if passMark < 0 or passMark > 100:
            raise forms.ValidationError('Pass mark should be between 0 and 100.')

        return passMark

    def clean_successText(self):
        successText = self.cleaned_data.get('successText')

        if not successText:
            raise forms.ValidationError('Text to display when passed should not be empty.')

        return successText

    def clean_failText(self):
        failText = self.cleaned_data.get('failText')

        if not failText:
            raise forms.ValidationError('Text to display when failed should not be empty.')

        return failText

    def clean_inRandomOrder(self):
        return self.cleaned_data.get('inRandomOrder')

    def clean_answerAtEnd(self):
        return self.cleaned_data.get('answerAtEnd')

    def clean_isExamPaper(self):
        maxAttempt = self.clean_maxAttempt()
        return maxAttempt is not None and int(maxAttempt) == 1 or self.data.get('isExamPaper') == 'on'

    def clean_isDraft(self):
        return self.cleaned_data.get('isDraft')

    def clean_enableAutoMarking(self):
        return self.cleaned_data.get('enableAutoMarking')

    def clean(self):
        raise NotImplementedError('Please implement clean() method')

    def save(self):
        raise NotImplementedError('Please implement save() method')

    def update(self):
        raise NotImplementedError('Please implement update() method')


class QuizCreateForm(QuizForm):

    def __init__(self, request, *args, **kwargs):
        super(QuizCreateForm, self).__init__(request, *args, **kwargs)
        self.request = request

    def clean(self):
        return self.cleaned_data

    def save(self):
        newQuiz = Quiz()
        newQuiz.name = self.cleaned_data.get('name')
        newQuiz.description = self.cleaned_data.get('description')
        newQuiz.subject = self.cleaned_data.get('subject')
        newQuiz.topic = self.cleaned_data.get('topic')
        newQuiz.quizDuration = self.cleaned_data.get('quizDuration')
        newQuiz.maxAttempt = self.cleaned_data.get('maxAttempt')
        newQuiz.difficulty = self.cleaned_data.get('difficulty')
        newQuiz.passMark = self.cleaned_data.get('passMark')
        newQuiz.successText = self.cleaned_data.get('successText')
        newQuiz.failText = self.cleaned_data.get('failText')
        newQuiz.inRandomOrder = self.cleaned_data.get('inRandomOrder')
        newQuiz.answerAtEnd = self.cleaned_data.get('answerAtEnd')
        newQuiz.isExamPaper = self.cleaned_data.get('isExamPaper')
        newQuiz.isDraft = self.cleaned_data.get('isDraft')
        newQuiz.enableAutoMarking = self.cleaned_data.get('enableAutoMarking')
        newQuiz.creator_id = self.request.user.id
        newQuiz.save()
        return newQuiz


class QuizUpdateForm(QuizForm):

    def __init__(self, request, quiz=None, *args, **kwargs):
        super(QuizUpdateForm, self).__init__(request, *args, **kwargs)
        self.request = request
        self.quiz = quiz

        if self.quiz is None or not isinstance(quiz, Quiz):
            raise Exception('Quiz is none, or is not an instance of Quiz object.')

        self.initial['name'] = quiz.name
        self.initial['description'] = quiz.description
        self.initial['subject'] = quiz.subject
        self.initial['topic'] = quiz.topic
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
        self.initial['enableAutoMarking'] = quiz.enableAutoMarking

        if quiz.creator_id != request.user.id:
            self.fields['name'].widget.attrs['disabled'] = True
            self.fields['description'].widget.attrs['disabled'] = True
            self.fields['subject'].widget.attrs['disabled'] = True
            self.fields['topic'].widget.attrs['disabled'] = True
            self.fields['quizDuration'].widget.attrs['disabled'] = True
            self.fields['maxAttempt'].widget.attrs['disabled'] = True
            self.fields['difficulty'].widget.attrs['disabled'] = True
            self.fields['passMark'].widget.attrs['disabled'] = True

            del self.fields['successText']
            del self.fields['failText']
            del self.fields['inRandomOrder']
            del self.fields['answerAtEnd']
            del self.fields['isExamPaper']
            del self.fields['isDraft']
            del self.fields['enableAutoMarking']

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if Quiz.objects.filter(name__iexact=name, creator=self.request.user).exclude(id=self.quiz.id).exists():
            raise forms.ValidationError(f'Quiz already exists with name: {name}')

        return name

    def clean(self):
        return self.cleaned_data

    def update(self):
        self.quiz.name = self.cleaned_data.get('name')
        self.quiz.description = self.cleaned_data.get('description')
        self.quiz.subject = self.cleaned_data.get('subject')
        self.quiz.topic = self.cleaned_data.get('topic')
        self.quiz.quizDuration = self.cleaned_data.get('quizDuration')
        self.quiz.maxAttempt = self.cleaned_data.get('maxAttempt')
        self.quiz.difficulty = self.cleaned_data.get('difficulty')
        self.quiz.passMark = self.cleaned_data.get('passMark')
        self.quiz.successText = self.cleaned_data.get('successText')
        self.quiz.failText = self.cleaned_data.get('failText')
        self.quiz.inRandomOrder = self.cleaned_data.get('inRandomOrder')
        self.quiz.answerAtEnd = self.cleaned_data.get('answerAtEnd')
        self.quiz.isExamPaper = self.cleaned_data.get('isExamPaper')
        self.quiz.isDraft = self.cleaned_data.get('isDraft')
        self.quiz.enableAutoMarking = self.cleaned_data.get('enableAutoMarking')
        self.quiz.save()
        return self.quiz


class QuestionForm(forms.Form):
    figure = forms.ImageField(
        label='Figure (Optional)',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
                'accept': 'image/*',
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
                'min': '0',
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

    def clean(self):
        figure = self.cleaned_data.get('figure')
        content = self.cleaned_data.get('content')
        mark = self.cleaned_data.get('mark')

        if not figure and not content:
            self.errors['figure'] = self.error_class(['Cannot leave both figure and content empty.'])
            self.errors['content'] = self.error_class(['Cannot leave both figure and content empty.'])

        if mark < 0:
            self.errors['mark'] = self.error_class(['Mark cannot be a negative number.'])

        return self.cleaned_data

    def save(self):
        raise NotImplementedError('Please implement save() method')

    def update(self):
        raise NotImplementedError('Please implement update() method')


class EssayQuestionCreateForm(QuestionForm):
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

    def __init__(self, quiz, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        self.quiz = quiz
        super().__init__(*args, **kwargs)

    def clean_answer(self):
        answer = self.cleaned_data.get('answer')

        if not answer:
            raise forms.ValidationError('Answer should not be empty.')

        return answer

    def clean(self):
        return super().clean()

    def save(self):
        question = Question.objects.create(
            quiz=self.quiz,
            figure=self.cleaned_data.get('figure'),
            content=self.cleaned_data.get('content'),
            explanation=self.cleaned_data.get('explanation'),
            mark=self.cleaned_data.get('mark'),
            questionType=Question.Type.ESSAY,
            answer=self.cleaned_data.get('answer'),
        )
        return question


class MultipleChoiceQuestionCreateForm(QuestionForm):
    choiceOrder = forms.ChoiceField(
        label='Choice Order',
        choices=[(None, '-- Select a value --')] + Question.ChoiceOrder.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    choiceType = forms.ChoiceField(
        label='Choice Type',
        choices=[(None, '-- Select a value --')] + Question.ChoiceType.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    choices = forms.JSONField(
        required=False,
        widget=forms.HiddenInput
    )

    def __init__(self, quiz, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        self.quiz = quiz
        super().__init__(*args, **kwargs)

    def clean_choiceOrder(self):
        choiceOrder = self.cleaned_data.get('choiceOrder')

        if choiceOrder not in Question.ChoiceOrder.values:
            raise forms.ValidationError('Select a choice order from the list provided.')

        return choiceOrder

    def clean_choiceType(self):
        choiceType = self.cleaned_data.get('choiceType')

        if choiceType not in Question.ChoiceType.values:
            raise forms.ValidationError('Select a choice type from the list provided.')

        return choiceType

    def clean_choices(self):
        choices = self.cleaned_data.get('choices')
        for choice in choices:
            if not choice.get('id'):
                choice['id'] = generalOperations.generateRandomString(8)
        self.initial['choices'] = choices
        return choices

    def clean(self):
        return super().clean()

    def save(self):
        question = Question.objects.create(
            quiz=self.quiz,
            figure=self.cleaned_data.get('figure'),
            content=self.cleaned_data.get('content'),
            explanation=self.cleaned_data.get('explanation'),
            mark=self.cleaned_data.get('mark'),
            questionType=Question.Type.MULTIPLE_CHOICE,
            choiceOrder=self.cleaned_data.get('choiceOrder'),
            choiceType=self.cleaned_data.get('choiceType'),
            choices={'choices': self.cleaned_data.get('choices', [])}
        )
        return question


class TrueOrFalseQuestionCreateForm(QuestionForm):
    trueOrFalse = forms.ChoiceField(
        label='Is the answer True or False?',
        choices=Question.TrueOrFalse.choices,
        required=True,
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-check-input',
                'style': 'height: 34px; width: 34px',
                'required': 'required',
            }
        )
    )

    def __init__(self, quiz, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        self.quiz = quiz
        super().__init__(*args, **kwargs)

    def clean(self):
        return super().clean()

    def save(self):
        question = Question.objects.create(
            quiz=self.quiz,
            figure=self.cleaned_data.get('figure'),
            content=self.cleaned_data.get('content'),
            explanation=self.cleaned_data.get('explanation'),
            mark=self.cleaned_data.get('mark'),
            questionType=Question.Type.TRUE_OR_FALSE,
            trueOrFalse=self.cleaned_data.get('trueOrFalse')
        )
        return question


class EssayQuestionUpdateForm(QuestionForm):
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

    def __init__(self, question=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.question = question

        if self.question is None or self.question.questionType != Question.Type.ESSAY:
            raise Exception('Question object is none, or is not compatible with EssayQuestionUpdateForm.')

        self.initial['figure'] = self.question.figure
        self.initial['content'] = self.question.content
        self.initial['explanation'] = self.question.explanation
        self.initial['mark'] = self.question.mark
        self.initial['answer'] = self.question.answer

    def clean_answer(self):
        answer = self.cleaned_data.get('answer')

        if not answer:
            raise forms.ValidationError('Answer should not be empty.')

        return answer

    def clean(self):
        return super().clean()

    def update(self):
        self.question.figure = self.cleaned_data.get('figure')
        self.question.content = self.cleaned_data.get('content')
        self.question.explanation = self.cleaned_data.get('explanation')
        self.question.mark = self.cleaned_data.get('mark')
        self.question.answer = self.cleaned_data.get('answer')
        self.question.save()
        return self.question


class TrueOrFalseQuestionUpdateForm(QuestionForm):
    trueOrFalse = forms.ChoiceField(
        label='Is the answer True or False?',
        choices=Question.TrueOrFalse.choices,
        initial=None,
        required=True,
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-check-input',
                'style': 'height: 34px; width: 34px',
                'required': 'required',
            }
        )
    )

    def __init__(self, question=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.question = question

        if self.question is None or self.question.questionType != Question.Type.TRUE_OR_FALSE:
            raise Exception('Question object is none, or is not compatible with TrueOrFalseQuestionUpdateForm.')

        self.initial['figure'] = self.question.figure
        self.initial['content'] = self.question.content
        self.initial['explanation'] = self.question.explanation
        self.initial['mark'] = self.question.mark
        self.initial['trueOrFalse'] = self.question.trueOrFalse

    def clean(self):
        return super().clean()

    def update(self):
        self.question.figure = self.cleaned_data.get('figure')
        self.question.content = self.cleaned_data.get('content')
        self.question.explanation = self.cleaned_data.get('explanation')
        self.question.mark = self.cleaned_data.get('mark')
        self.question.trueOrFalse = self.cleaned_data.get('trueOrFalse')
        self.question.save()
        return self.question


class MultipleChoiceQuestionUpdateForm(QuestionForm):
    choiceOrder = forms.ChoiceField(
        label='Choice Order',
        choices=[(None, '-- Select a value --')] + Question.ChoiceOrder.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    choiceType = forms.ChoiceField(
        label='Choice Type',
        choices=[(None, '-- Select a value --')] + Question.ChoiceType.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%; border-radius: 0',
                'required': 'required',
            }
        ),
    )
    choices = forms.JSONField(
        required=True,
        widget=forms.HiddenInput
    )

    def __init__(self, question=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.question = question

        if self.question is None or self.question.questionType != Question.Type.MULTIPLE_CHOICE:
            raise Exception('Question object is none, or is not compatible with MultipleChoiceQuestionUpdateForm.')

        self.initial['figure'] = self.question.figure
        self.initial['content'] = self.question.content
        self.initial['explanation'] = self.question.explanation
        self.initial['mark'] = self.question.mark
        self.initial['choiceOrder'] = self.question.choiceOrder
        self.initial['choiceType'] = self.question.choiceType
        self.initial['choices'] = self.question.choices.get('choices')

    def clean_choiceOrder(self):
        choiceOrder = self.cleaned_data.get('choiceOrder')

        if choiceOrder not in Question.ChoiceOrder.values:
            raise forms.ValidationError('Select a choice order from the list provided.')

        return choiceOrder

    def clean_choiceType(self):
        choiceType = self.cleaned_data.get('choiceType')

        if choiceType not in Question.ChoiceType.values:
            raise forms.ValidationError('Select a choice type from the list provided.')

        return choiceType

    def clean_choices(self):
        choices = self.cleaned_data.get('choices')
        for choice in choices:
            if not choice.get('id'):
                choice['id'] = generalOperations.generateRandomString(8)
        self.initial['choices'] = choices
        return choices

    def clean(self):
        return super().clean()

    def update(self):
        self.question.figure = self.cleaned_data.get('figure')
        self.question.content = self.cleaned_data.get('content')
        self.question.explanation = self.cleaned_data.get('explanation')
        self.question.mark = self.cleaned_data.get('mark')
        self.question.choiceOrder = self.cleaned_data.get('choiceOrder')
        self.question.choiceType = self.cleaned_data.get('choiceType')
        self.question.choices = {'choices': self.cleaned_data.get('choices', [])}
        self.question.save()
        return self.question


class BaseResponseForm(forms.Form):

    def __init__(self, response, allowEdit=True, validateMark=False, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        self.response = response
        self.allowEdit = allowEdit
        self.setInitialValues(response)

        if not self.allowEdit:
            self.showSystemAnswerWhileMarking(response)
            self.disableFields()

        if validateMark:
            if response.mark:
                self.data['markResponseAlert'] = 'border border-success'
            else:
                self.data['markResponseAlert'] = 'border border-danger'
        else:
            self.data['markResponseAlert'] = 'border border-secondary'

    def setInitialValues(self, response):
        raise NotImplementedError('Please implement setInitialValues() method')

    def showSystemAnswerWhileMarking(self, response):
        raise NotImplementedError('Please implement showSystemAnswerWhileMarking() method')

    def disableFields(self):
        for field in self.fields.values():
            field.widget.attrs['disabled'] = 'disabled'


class EssayQuestionResponseForm(BaseResponseForm):
    answer = forms.CharField(
        label='<h5>Your Answer</h5>',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'rows': 5,
            }
        )
    )

    def setInitialValues(self, response):
        self.fields['answer'].initial = response.answer

    def showSystemAnswerWhileMarking(self, response):
        self.fields['systemAnswer'] = forms.CharField(
            label='<h5>System Answer</h5>',
            initial=response.question.answer,
            required=False,
            widget=forms.Textarea(
                attrs={
                    'class': 'form-control col',
                    'style': 'border-radius: 0',
                    'rows': 5,
                }
            )
        )


class TrueOrFalseQuestionResponseForm(BaseResponseForm):
    def setInitialValues(self, response):
        field = forms.ChoiceField(
            label='Is the answer True or False?' if self.allowEdit else 'Your Answer',
            required=False,
            choices=Question.TrueOrFalse.choices,
            initial=response.trueOrFalse,
            widget=forms.RadioSelect(
                attrs={
                    'class': 'form-check-input',
                    'style': 'height: 34px; width: 34px',
                }
            )
        )
        if not self.allowEdit:
            randomString = generalOperations.generateRandomString(3)
            self.fields[f'trueOrFalse_{randomString}'] = field
        else:
            self.fields['trueOrFalse'] = field

    def showSystemAnswerWhileMarking(self, response):
        randomString = generalOperations.generateRandomString(3)
        self.fields[f'systemAnswer_{randomString}'] = forms.ChoiceField(
            label='System Answer',
            required=False,
            choices=Question.TrueOrFalse.choices,
            initial=response.question.trueOrFalse,
            widget=forms.RadioSelect(
                attrs={
                    'class': 'form-check-input',
                    'style': 'height: 34px; width: 34px',
                }
            )
        )


class MultipleChoiceQuestionResponseForm(BaseResponseForm):
    def setInitialValues(self, response):
        style = {'style': 'height: 34px; width:34px'}

        if response.question.choiceType == Question.ChoiceType.SINGLE:
            widget = forms.RadioSelect(attrs=style)
            fieldName = f'options_{generalOperations.generateRandomString(3)}'
        else:
            widget = forms.CheckboxSelectMultiple(attrs=style)
            fieldName = 'options'

        self.fields[fieldName] = forms.MultipleChoiceField(
            label='Select the correct answer(s).' if self.allowEdit else 'Your Answer',
            choices=[(choice['id'], choice['content']) for choice in response.choices.get('choices')],
            initial=[choice['id'] for choice in response.choices.get('choices') if choice['isChecked']],
            widget=widget
        )

    def showSystemAnswerWhileMarking(self, response):
        style = {'style': 'height: 34px; width:34px'}
        if response.question.choiceType == Question.ChoiceType.SINGLE:
            widget = forms.RadioSelect(attrs=style)
        else:
            widget = forms.CheckboxSelectMultiple(attrs=style)
        self.fields[f'systemAnswer_{generalOperations.generateRandomString(3)}'] = forms.MultipleChoiceField(
            label='System Answer',
            choices=[(choice['id'], choice['content']) for choice in response.question.choices.get('choices')],
            initial=[choice['id'] for choice in response.question.choices.get('choices') if choice['isChecked']],
            widget=widget
        )
