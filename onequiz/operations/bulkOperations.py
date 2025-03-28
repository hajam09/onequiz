import uuid

from django.contrib import messages

from core.models import Question


def create_base_question(content, explanation, mark):
    question = Question()
    question.content = content
    question.explanation = explanation
    question.mark = mark
    return question


def create_essay_question(request, content, explanation, mark, answer):
    question = create_base_question(content, explanation, mark)
    question.questionType = Question.Type.ESSAY
    question.answer = answer
    return question


def create_multiple_choice_question(request, content, explanation, mark, choice_order, option_answers, options):
    question = create_base_question(content, explanation, mark)
    question.questionType = Question.Type.MULTIPLE_CHOICE

    if not choice_order.upper() in Question.ChoiceOrder.values:
        messages.error(
            request,
            f'''The choice_order {choice_order} is not a valid value.
            Must be either {" or ".join(Question.ChoiceOrder.values)}'''
        )
        return None

    for correct_answer in option_answers:
        if correct_answer not in options:
            messages.error(
                request,
                f'''The option(s) provided in option_answers are invalid.
                Ensure all values in option_answers correspond to the available options'''
            )
            return None

    question.choiceOrder = choice_order.upper()
    question.choiceType = Question.ChoiceType.SINGLE if len(option_answers) == 1 else Question.ChoiceType.MULTIPLE

    choices = [
        {
            'id': uuid.uuid4().hex,
            'content': value,
            'isChecked': key in option_answers
        }
        for key, value in options.items()
    ]
    question.choices = {'choices': choices}
    return question


def create_true_or_false_question(request, content, explanation, mark, true_or_false):
    question = create_base_question(content, explanation, mark)
    question.questionType = Question.Type.TRUE_OR_FALSE

    if not true_or_false.upper() in Question.TrueOrFalse.values:
        messages.error(
            request,
            f'''The choice_order {true_or_false} is not a valid value.
            Must be either {" or ".join(Question.TrueOrFalse.values)}'''
        )
        return None

    question.trueOrFalse = true_or_false.upper()
    return question
