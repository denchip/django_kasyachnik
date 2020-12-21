from django.http import JsonResponse
from django.views import View
from django.conf import settings
from kasyachnik.users.models import User, create_user_from_weebhook
import json


# https://api.telegram.org/bot<token>/setWebhook?url=<url>
class WebHookView(View):
    def post(self, request, *args, **kwargs):
        import sys
        t_data = json.loads(request.body)
        from_id = t_data['message']['from']['id']
        if not User.objects.filter(telegram_id=from_id).exists():
            create_user_from_weebhook(request_data=t_data)

        return JsonResponse({"ok": "POST request processed"})
