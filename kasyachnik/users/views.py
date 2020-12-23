from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.template import loader
from django.http import HttpResponse
from kasyachnik.users.models import User
from kasyachnik.bot.models import Chat, Bets, BetsOption, BetsStatus
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
        chat = Chat.objects.filter(telegram_id=chat_id).first()
        if not chat:
            return HttpResponse('Некорректные данные чата', status=400)

        if Bets.objects.filter(chat=chat, status=BetsStatus.OPENED.value).exists():
            return HttpResponse('В данном чате уже проводится событие', status=404)

        bets_name = request.data.get('bets_name', None)
        bets_obj = Bets.objects.create(initiator=user, chat=chat, title=bets_name)
        bets = []
        bets_msg = ''

        for key, value in request.data.items():
            if key.startswith('bet_'):
                bets.append(value)
                try:
                    BetsOption.objects.create(bets=bets_obj, title=value, number=len(bets))
                except:
                    return HttpResponse('Некорректное значение варианта ставки', status=404)
                bets_msg += f'{len(bets)}. {value}\n'
        if chat_id and bets_name and len(bets):
            username = user.telegram_username or user.username
            msg_text = f'@{username} создал ставочку `{bets_name}`. Вариантики: \n{bets_msg}\n ' \
                       f'`/bet {{НОМЕР}} {{СКОЛЬКО СТАВИТЬ}}`'
            bot.send_message(msg_text, chat_id=chat_id)

        return HttpResponse('Успешно создано')
