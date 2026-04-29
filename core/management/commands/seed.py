import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from faker import Faker

from core.models import (
    Question,
    Quiz,
    QuizAttempt,
    Response,
    Result,
)
from onequiz.operations import bakerOperations
from settings.models import UserNotificationSettings

faker = Faker('en_GB')


class Command(BaseCommand):
    NUMBER_OF_USERS = 1
    NUMBER_OF_QUIZ = 10
    NUMBER_OF_QUESTIONS_PER_QUIZ = 10

    def handle(self, *args, **kwargs):
        # -----------------------------
        # CLEAN DB
        # -----------------------------
        Result.objects.all().delete()
        Response.objects.all().delete()
        QuizAttempt.objects.all().delete()
        UserNotificationSettings.objects.all().delete()
        Question.objects.all().delete()
        Quiz.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # -----------------------------
        # CREATE USERS
        # -----------------------------
        bakerOperations.createUsers(self.NUMBER_OF_USERS)
        users = list(User.objects.all())

        # -----------------------------
        # CREATE QUIZZES
        # -----------------------------
        quizList = [
            bakerOperations.createQuiz(creator=random.choice(users), save=False)
            for _ in range(self.NUMBER_OF_QUIZ)
        ]
        Quiz.objects.bulk_create(quizList)

        quizList = list(Quiz.objects.prefetch_related("questions"))

        # -----------------------------
        # CREATE QUESTIONS
        # -----------------------------
        questions = []
        for quiz in quizList:
            questions.extend(
                bakerOperations.createRandomQuestions(
                    quiz,
                    self.NUMBER_OF_QUESTIONS_PER_QUIZ,
                    False
                )
            )

        Question.objects.bulk_create(questions)

        # -----------------------------
        # NOTIFICATIONS
        # -----------------------------
        notifications = [
            bakerOperations.createUserNotifications(user, False)
            for user in users
        ]
        UserNotificationSettings.objects.bulk_create(notifications)

        # -----------------------------
        # MAIN FLOW
        # -----------------------------
        self.create_quiz_attempts(users, quizList)
        self.quiz_attempt_submission_flow()

    # =========================================================
    # CREATE QUIZ ATTEMPTS (FIXED)
    # =========================================================
    def create_quiz_attempts(self, users, quizList):
        quizAttempts = []
        user_pool = list(users)

        for quiz in quizList:
            available_users = [u for u in user_pool if u.id != quiz.creator_id]

            for _ in range(random.randint(2, 10)):
                quizAttempts.append(
                    QuizAttempt(
                        quiz=quiz,
                        user=random.choice(available_users),
                        status=QuizAttempt.Status.IN_PROGRESS
                    )
                )

        # STEP 1: save attempts first (IMPORTANT FIX)
        QuizAttempt.objects.bulk_create(quizAttempts)

        # STEP 2: reload with IDs + relations
        quizAttempts = list(
            QuizAttempt.objects.select_related("quiz").prefetch_related("quiz__questions")
        )

        # STEP 3: create responses safely
        responses = []

        for qa in quizAttempts:
            questions = list(qa.quiz.questions.all())

            for q in questions:
                responses.append(
                    Response(
                        question=q,
                        quizAttempt=qa
                    )
                )

        Response.objects.bulk_create(responses, batch_size=500)

    # =========================================================
    # SUBMISSION FLOW (OPTIMIZED + SAFE)
    # =========================================================
    def quiz_attempt_submission_flow(self):
        all_attempts = list(
            QuizAttempt.objects.select_related("quiz")
        )

        in_progress, submitted, marked = self.split_into_three(all_attempts)

        submitted_ids = [a.id for a in submitted]
        marked_ids = [a.id for a in marked]

        # -----------------------------
        # LOAD ALL RESPONSES ONCE
        # -----------------------------
        responses = list(
            Response.objects.select_related("question", "quizAttempt")
        )

        # group by attempt
        response_map = {}
        for r in responses:
            response_map.setdefault(r.quizAttempt_id, []).append(r)

        # -----------------------------
        # UPDATE RESPONSES
        # -----------------------------
        modified = []

        for r in responses:
            q = r.question

            if q.questionType == Question.Type.ESSAY:
                r.answer = faker.paragraph()

            elif q.questionType == Question.Type.TRUE_OR_FALSE:
                r.trueOrFalse = random.choice(Question.TrueOrFalse.values)

            elif q.questionType == Question.Type.MULTIPLE_CHOICE:
                choices = r.choices or []

                if q.choiceType == Question.ChoiceType.SINGLE:
                    if choices:
                        selected = random.randrange(len(choices))
                        for i, c in enumerate(choices):
                            c["isChecked"] = (i == selected)

                elif q.choiceType == Question.ChoiceType.MULTIPLE:
                    for c in choices:
                        c["isChecked"] = random.choice([True, False])

                r.choices = choices

            modified.append(r)

        Response.objects.bulk_update(
            modified,
            fields=["answer", "trueOrFalse", "choices"],
            batch_size=500
        )

        # -----------------------------
        # STATUS UPDATE
        # -----------------------------
        QuizAttempt.objects.filter(id__in=submitted_ids).update(
            status=QuizAttempt.Status.SUBMITTED
        )

        QuizAttempt.objects.filter(id__in=marked_ids).update(
            status=QuizAttempt.Status.MARKED
        )

        # -----------------------------
        # MARKING
        # -----------------------------
        marked_responses = [
            r for r in responses if r.quizAttempt_id in marked_ids
        ]

        for r in marked_responses:
            r.mark = random.randint(0, r.question.mark)

        Response.objects.bulk_update(
            marked_responses,
            fields=["mark"],
            batch_size=500
        )

        # -----------------------------
        # RESULTS
        # -----------------------------
        result_list = []

        for attempt in marked:
            attempt_responses = response_map.get(attempt.id, [])

            correct = partial = wrong = 0
            total_awarded = 0
            total_possible = 0

            for r in attempt_responses:
                if r.mark == r.question.mark:
                    correct += 1
                elif r.mark and r.mark < r.question.mark:
                    partial += 1
                else:
                    wrong += 1

                total_awarded += float(r.mark or 0)
                total_possible += r.question.mark

            score = round((total_awarded / total_possible) * 100, 2) if total_possible else 0

            result_list.append(
                Result(
                    quizAttempt=attempt,
                    timeSpent=random.randint(1, attempt.quiz.quizDuration),
                    numberOfCorrectAnswers=correct,
                    numberOfPartialAnswers=partial,
                    numberOfWrongAnswers=wrong,
                    score=score
                )
            )

        Result.objects.bulk_create(result_list)

    # =========================================================
    # UTIL
    # =========================================================
    def split_into_three(self, lst):
        n = len(lst)
        k, m = divmod(n, 3)

        return [
            lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
            for i in range(3)
        ]
