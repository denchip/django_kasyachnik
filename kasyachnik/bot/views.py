from django.http import JsonResponse
from django.views import View
from kasyachnik.users.models import get_or_create_user
from kasyachnik.bot.models import Message, get_or_create_chat, save_message
from kasyachnik.bot.singleton import bot
import json


class WebHookView(View):
    def post(self, request, *args, **kwargs):
        t_data = json.loads(request.body)
        message = None

        if 'message' in t_data:
            message = t_data['message']
        if 'edited_message' in t_data:
            message = t_data['edited_message']

        if message:
            user = get_or_create_user(message=message)
            chat = get_or_create_chat(message=message)
            if chat and not chat.participants.filter(telegram_id=user.telegram_id).exists():
                chat.participants.add(user)
            save_message(user=user, chat=chat, message=message)
        return JsonResponse({"ok": "POST request processed"})
