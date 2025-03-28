import os
import random
import uuid

from django.core.management import BaseCommand
from faker import Faker

from core.models import (
    Question,
    Quiz
)

BOOLEAN = [True, False]

import json


class Command(BaseCommand):
    help = 'Create Baker Model'
    NUMBER_OF_QUIZ = 300

    def handle_json_file(self):
        file_path = os.path.join(os.path.dirname(__file__), 'q.json')

        with open(file=file_path, mode='r') as file:
            data = json.load(file)

        for content in data:
            question_text = content.get('question')
            if Question.objects.filter(content=question_text).exists():
                print(f'Question "{question_text}" already exists.')

            question = Question()
            question.figure = None
            question.content = question_text
            question.explanation = content.get('explanation')
            question.mark = content.get('mark', 1)

    def handle(self, *args, **kwargs):
        # if Question.objects.filter(content=question_text).exists()
        #     pass

        # MyModel.objects.filter(field_name__icontains='search_value')

        aa = 1
        # with open(file=file_path, mode='r', encoding="utf8") as file:
        #     for line in file:
        #         line_striped = line.strip()
        #
        #         if not line_striped:
        #             continue
        #
        #         aa = 1

        QUESTION_LIST = []
        has_error = False
        faker = Faker()
        file_path = os.path.join(os.path.dirname(__file__), 'data.txt', )
        with open(file=file_path, mode='r', encoding="utf8") as file:
            file_content = file.read()

        lines = file_content.split('Q: ')
        quiz = Quiz.objects.get(id=1)
        for line in lines:
            each_line = line.split('\n')[:-1]
            if not each_line:
                continue

            question_text = each_line[0]
            correct_answer = ''.join(
                each_line[-1].replace('Correct_answer: ', '').strip().lstrip().rstrip().split()).split(',')

            for selected_option in correct_answer:
                if len(selected_option) != 1:
                    has_error = True
                    print('selected options is wrong for question', question_text)

            if len(correct_answer) == 0:
                has_error = True
                print('incorrect question format')

            if Question.objects.filter(content=question_text).exists():
                continue
            else:
                aa = 1

            choices = []
            for choice in each_line[1:-1]:
                opt_split = choice.split('.')
                try:

                    choices.append({
                        'id': opt_split[0],
                        'content': '.'.join(opt_split[1:]),
                        'isChecked': opt_split[0] in correct_answer
                    })
                except:
                    aa = 1

            question = Question()
            question.figure = None
            question.content = question_text
            question.explanation = None
            question.mark = faker.random_number(digits=2)
            question.questionType = Question.Type.MULTIPLE_CHOICE
            question.choiceOrder = random.choice(
                [Question.ChoiceOrder.SEQUENTIAL, Question.ChoiceOrder.RANDOM, Question.ChoiceOrder.NONE]
            )
            question.choiceType = Question.ChoiceType.SINGLE if len(
                correct_answer) == 1 else Question.ChoiceType.MULTIPLE

            for up in choices:
                up['id'] = uuid.uuid4().hex

            question.choices = {'choices': choices}

            QUESTION_LIST.append(question)

        if not has_error:
            Question.objects.bulk_create(QUESTION_LIST)

        # with transaction.atomic():
        quiz.questions.add(*QUESTION_LIST)
