from enum import Enum


class FeatureFlag:
    def __init__(self, name, description, enabledFl):
        self.name = name
        self.description = description
        self.enabledFl = enabledFl


class FeatureFlagType(Enum):
    SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT = 'SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT'
    ESSAY_QUESTION_IN_QUIZ_ATTEMPT = 'ESSAY_QUESTION_IN_QUIZ_ATTEMPT'


featureFlagList = [
    FeatureFlag(FeatureFlagType.SAVE_QUIZ_ATTEMPT_RESPONSE_AS_DRAFT, '', False),
    FeatureFlag(FeatureFlagType.ESSAY_QUESTION_IN_QUIZ_ATTEMPT, '', False),
]


class FeatureFlagUtils:
    def __init__(self):
        self.featureFlags = featureFlagList

    def isEnabled(self, flagName):

        for flag in self.featureFlags:
            if flag.name == flagName:
                return flag.enabledFl

        raise Exception('Unknown FeatureFlag', flagName)


featureFlagOperations = FeatureFlagUtils()
