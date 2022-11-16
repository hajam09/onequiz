import os
import random
import re

from django.conf import settings


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
