from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.template import loader
from django.http import HttpResponse
from kasyachnik.users.models import User
from kasyachnik.bot.models import Chat
from kasyachnik.bot.singleton import bot


class LoginView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        template = loader.get_template('index.html')
        return HttpResponse(template.render({}, request))


class BetsView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('id', None)

        if not telegram_id:
            return HttpResponse('Не удалось авторизоваться', status=403)
        user = User.objects.filter(telegram_id=telegram_id).first()
        if not user:
            return HttpResponse('Не удалось авторизоваться', status=403)

        chats = Chat.objects.filter(participants=user)
        template = loader.get_template('bets.html')
        context = {'chats': chats}
        return HttpResponse(template.render(context, request))

    def post(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('id', None)

        if not telegram_id:
            return HttpResponse('Не удалось авторизоваться', status=403)
        user = User.objects.filter(telegram_id=telegram_id).first()
        if not user:
            return HttpResponse('Не удалось авторизоваться', status=403)

        chat_id = request.data.get('chat', None)
        bets_name = request.data.get('bets_name', None)
        bets = []
        bets_msg = ''
        for key, value in request.data.items():
            if key.startswith('bet_'):
                bets.append(value)
                bets_msg += f'{len(bets)}. {value}\n'
        if chat_id and bets_name and len(bets):
            username = user.telegram_username or user.username
            msg_text = f'{username} создал ставочку `{bets_name}`. Вариантики: \n{bets_msg}\n ' \
                       f'Для ставки используйте команду `/bet {{НОМЕР}} {{СКОЛЬКО СТАВИТЬ}}`'
            bot.send_message(msg_text, chat_id=chat_id)

        return HttpResponse('Успешно создано')
