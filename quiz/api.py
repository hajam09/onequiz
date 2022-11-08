from http import HTTPStatus

from django.db.models import F
from django.http import JsonResponse
from django.views import View

from quiz.models import Topic


class TopicObjectApiEventVersion1Component(View):
    def get(self, *args, **kwargs):
        topics = Topic.objects.filter(**self.request.GET.dict()).annotate(
            _id=F('id'), _name=F('name'), _description=F('description')
        ).values('id', 'name', 'description')

        response = {
            "success": True,
            "data": {
                "topics": list(topics)
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)
