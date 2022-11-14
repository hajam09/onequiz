import random

from django.conf import settings
from django.contrib.auth.models import User
from faker import Faker

EMAIL_DOMAINS = ["@yahoo", "@gmail", "@outlook", "@hotmail"]
DOMAINS = [".co.uk", ".com", ".co.in", ".net", ".us"]


def createUsers(limit=20, maxLimit=20, save=True):
    currentCount = User.objects.count()
    remaining = maxLimit - currentCount

    if limit == 0 or currentCount > maxLimit:
        return User.objects.all()[:limit]

    BULK_USERS = []
    uniqueEmails = []
    for _ in range(remaining):
        fake = Faker()
        firstName = fake.unique.first_name()
        lastName = fake.unique.last_name()
        email = firstName.lower() + '.' + lastName.lower() + random.choice(EMAIL_DOMAINS) + random.choice(DOMAINS)
        user = User(username=email, email=email, first_name=firstName, last_name=lastName)
        user.set_password(settings.TEST_PASSWORD)
        BULK_USERS.append(user)
        uniqueEmails.append(email)

    if save:
        User.objects.bulk_create(BULK_USERS)
        return User.objects.filter(email__in=uniqueEmails)

    return BULK_USERS


def createUser(save=True):
    userList = createUsers(1, 2, save)
    return userList.first() if save else userList[0]
