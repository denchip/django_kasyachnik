from django.http import JsonResponse
from django.views import View
from kasyachnik.users.models import get_or_create_user
from kasyachnik.bot.models import Message, get_or_create_chat, save_message
from kasyachnik.bot.singleton import bot


class WebHookView(View):
    def post(self, request, *args, **kwargs):
        bot.process_request(request=request)
        return JsonResponse({"ok": "POST request processed"})
