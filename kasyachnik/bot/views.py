from django.http import JsonResponse
from django.views import View
from django.conf import settings
from kasyachnik.users.models import User
import json


# https://api.telegram.org/bot<token>/setWebhook?url=<url>
class WebHookView(View):
    def post(self, request, *args, **kwargs):
        import sys
        t_data = json.loads(request.body)
        return JsonResponse({"ok": "POST request processed"})
