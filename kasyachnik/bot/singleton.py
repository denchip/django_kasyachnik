from django.conf import settings
from django.db.models import Sum
from kasyachnik.users.models import get_or_create_user
from kasyachnik.bot.models import get_or_create_chat, save_message, Bets, BetsOption, BetsStatus, Bet
import requests
import json


class Kasyachnik:
    __instance = None

    def __init__(self):
        if not Kasyachnik.__instance:
            self.save_messages = True
            self.commands_prefix = '/'
            self.commands_list = ['banek', 'shama', 'bet', 'betstatus']
        else:
            self.get_instance()

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Kasyachnik()
        return cls.__instance

    def send_message(self, message, chat_id=None, reply_to_msg_id=None, parse_mode="Markdown"):
        if not chat_id:
            if self._chat:
                chat_id = self._chat.telegram_id
            else:
                chat_id = self._user.telegram_id
        if not reply_to_msg_id:
            if hasattr(self, '_message_obj') and self._message_obj:
                reply_to_msg_id = self._message_obj.telegram_id
        data = {
            "chat_id": chat_id,
            "text": message,
            "reply_to_message_id": reply_to_msg_id,
            "parse_mode": parse_mode,
        }
        response = requests.post(
            f"{settings.TELEGRAM_URL}{settings.TELEGRAM_BOT_TOKEN}/sendMessage", data=data
        )
        return response

    def _pre_process_request(self, request=None):
        request_json = json.loads(request.body)
        message = None

        if 'message' in request_json:
            message = request_json['message']
        if 'edited_message' in request_json:
            message = request_json['edited_message']

        if message:
            user = get_or_create_user(message=message)
            chat = get_or_create_chat(message=message)
            if chat and not chat.participants.filter(telegram_id=user.telegram_id).exists():
                chat.participants.add(user)
            if hasattr(self, 'save_messages') and self.save_messages:
                self._message_obj = save_message(user=user, chat=chat, message=message)
            self._user = user
            self._chat = chat
            self._message = message

    def _post_process_request(self):
        pass

    def _process_command(self, command=None, args_string=None):
        if not hasattr(self, 'commands_list') or command not in self.commands_list:
            self.send_message('Необработанная команда')
        # elif command == 'banek':
        #     response = requests.get('https://baneks.ru/random')
        #     text = response.text.split('<p>')[1].split('</p>')[0].replace('<br />', '\n').encode('ISO-8859-1').decode(
        #         'utf-8')
        #     self.send_message(text)
        elif command == 'bet':
            try:
                number, amount = args_string.split()
                number = int(number)
                amount = int(amount)
            except:
                self.send_message('Некорректное значение ставки.\nИспользуйте /bet {НОМЕР} {СКОЛЬКО СТАВИТЬ}')
                return

            if self._user.coins < amount:
                self.send_message('Браток, у тебя нет столько денег, приходи, когда станешь побогаче')
                return
            bets_obj = Bets.objects.filter(chat=self._chat, status=BetsStatus.OPENED.value).first()
            if not bets_obj:
                self.send_message('Эй, лудоман поехавший, сейчас нет активных ставок')
                return
            bet_option_obj = BetsOption.objects.filter(bets=bets_obj, number=number).first()
            if not bet_option_obj:
                self.send_message('Такого варианта нет в данной ставочке')
                return
            try:
                Bet.objects.create(bettor=self._user, amount=amount, bets=bet_option_obj)
                self._user.coins -= amount
                self._user.save()
                self.send_message(f'Ставочка на `{amount}` приколдезов на вариант `{bet_option_obj.title}` принята. '
                                  f'Лол, удачи')
            except:
                self.send_message('Не удалось сделать ставку')
        elif command == 'betstatus':
            bets_obj = Bets.objects.filter(chat=self._chat, status=BetsStatus.OPENED.value).first()
            if not bets_obj:
                self.send_message('Эй, лудоман поехавший, сейчас нет активных ставок')
                return
            bet_options = BetsOption.objects.filter(bets=bets_obj).order_by('number')
            msg = ''
            all_bets_sum = 0
            for bet_option in bet_options:
                one_bet = Bet.objects.filter(bets=bet_option).aggregate(Sum('amount'))['amount__sum']
                if one_bet:
                    all_bets_sum += one_bet
            for bet_option in bet_options:
                bet_sum = Bet.objects.filter(bets=bet_option).aggregate(Sum('amount'))['amount__sum']
                if bet_sum:
                    rate = round(all_bets_sum / bet_sum, 2)
                    msg += f'{bet_option.number}. `{bet_option.title}`. Залито: `{bet_sum}`. Текущий коэффициент: ' \
                           f'`{rate}`\n'
            self.send_message(msg)

    def process_message(self, message=None):
        if hasattr(self, 'commands_prefix'):
            if message.startswith(self.commands_prefix):
                try:
                    command, args = message.split(self.commands_prefix)[1].split(maxsplit=1)
                    self._process_command(command=command, args_string=args)
                except ValueError:
                    try:
                        command = message.split(self.commands_prefix)[1]
                        self._process_command(command=command)
                    except ValueError:
                        self.send_message('Некорректный синтаксис')

    def process_request(self, request=None):
        self._pre_process_request(request=request)
        if self._message and 'text' in self._message:
            self.process_message(message=self._message['text'])
        self._post_process_request()


bot = Kasyachnik.get_instance()
