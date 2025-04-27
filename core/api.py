import random

from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response as DRFResponse
from rest_framework.views import APIView

from core.models import (
    QuizAttempt,
    Quiz,
    Response
)


class QuizAttemptCommenceApiVersion1(APIView):
    def post(self, request, *args, **kwargs):
        quizId = self.request.data.get('quizId')
        user = self.request.user

        existingInProgressAttempt = QuizAttempt.objects.filter(
            quiz_id=quizId,
            user=user,
            status=QuizAttempt.Status.IN_PROGRESS
        ).first()

        if existingInProgressAttempt:
            response = {
                'success': True,
                'redirectUrl': reverse('core:quiz-attempt-view-v1', kwargs={'url': existingInProgressAttempt.url})
            }
            return DRFResponse(response, status=status.HTTP_200_OK)

        totalAttempts = QuizAttempt.objects.filter(
            quiz_id=quizId,
            user=user
        ).count()

        quiz = Quiz.objects.get(id=quizId, isDraft=False)
        if totalAttempts >= quiz.maxAttempt:
            response = {
                'success': False,
                'message': 'Maximum attempts reached for this quiz.'
            }
            messages.info(
                request, 'Maximum attempts reached for this quiz.'
            )
            return DRFResponse(response, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            quizAttempt = QuizAttempt.objects.create(
                quiz=quiz,
                user=user,
                status=QuizAttempt.Status.IN_PROGRESS
            )
            responseList = [
                Response(question=question, quizAttempt=quizAttempt)
                for question in quiz.questions.all()
            ]
            Response.objects.bulk_create(responseList)
            if quiz.inRandomOrder:
                random.shuffle(responseList)

            cache.set(
                f'quiz-attempt-v1-{quizAttempt.url}',
                [response.url for response in responseList],
                quizAttempt.quiz.quizDuration * 60 + 30
            )

        response = {
            'success': True,
            'redirectUrl': reverse('core:quiz-attempt-view-v1', kwargs={'url': quizAttempt.url})
        }
        return DRFResponse(response, status=status.HTTP_200_OK)
