import os
import random
import re

from django.conf import settings

from quiz.models import EssayQuestion, MultipleChoiceQuestion, TrueOrFalseQuestion


def isPasswordStrong(password):
    if len(password) < 8:
        return False

    if not any(letter.isalpha() for letter in password):
        return False

    if not any(capital.isupper() for capital in password):
        return False

    if not any(number.isdigit() for number in password):
        return False

    return True


def getRandomAvatar():
    return "avatars/" + random.choice(os.listdir(os.path.join(settings.MEDIA_ROOT, "avatars/")))


def deleteImage(imageField):
    if imageField is None:
        return

    existingImage = os.path.join(settings.MEDIA_ROOT, imageField.name)
    try:
        if os.path.exists(existingImage) and "/media/avatars/" not in imageField.url:
            os.remove(existingImage)
    except ValueError:
        pass


def parseStringToUrl(link):
    link = re.sub('\s+', '-', link).lower()
    link = ''.join(letter for letter in link if letter.isalnum() or letter == '-')
    return link


class QuestionAndResponse:

    def __init__(self, questionList, responseList):
        self.questionList = questionList
        self.responseList = responseList

    def getResponse(self):
        computedResponseList = [
            self.getResponseForQuestion(question) for question in self.questionList
        ]
        return computedResponseList

    def getResponseForQuestion(self, question):
        data = {
            'id': question.id,
            'figure': None,
            'content': question.content,
            'explanation': question.explanation,
        }

        additionalData = {}
        if isinstance(question, EssayQuestion):
            additionalData = self.getEssayQuestionResponse(question)
        elif isinstance(question, TrueOrFalseQuestion):
            additionalData = self.getTrueOrFalseQuestionResponse(question)
        elif isinstance(question, MultipleChoiceQuestion):
            additionalData = self.getMultipleChoiceQuestionResponse(question)
        else:
            pass

        try:
            mergedData = data | additionalData
        except TypeError:
            mergedData = {**data, **additionalData}

        return mergedData

    def getResponseObject(self, question):
        return next((o for o in self.responseList if o.question.id == question.id))

    def getEssayQuestionResponse(self, question):
        responseObject = self.getResponseObject(question)
        data = {
            'type': 'EssayQuestion',
            'response': {
                'id': responseObject.essayresponse.id,
                'text': responseObject.essayresponse.answer
            }
        }
        return data

    def getTrueOrFalseQuestionResponse(self, question):
        responseObject = self.getResponseObject(question)
        data = {
            'type': 'TrueOrFalseQuestion',
            'response': {
                'id': responseObject.trueorfalseresponse.id,
                'selectedOption': responseObject.trueorfalseresponse.isChecked
            }
        }
        return data

    def getMultipleChoiceQuestionResponse(self, question):
        responseObject = self.getResponseObject(question)
        data = {
            'type': 'MultipleChoiceQuestion',
            'response': {
                'id': responseObject.multiplechoiceresponse.id,
                'choices': [
                    {
                        'id': answer['id'],
                        'content': answer['content'],
                        'isChecked': answer['isChecked']
                    }
                    for answer in responseObject.multiplechoiceresponse.answers['answers']
                ]
            }
        }
        return data
