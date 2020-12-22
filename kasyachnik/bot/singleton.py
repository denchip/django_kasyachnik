from django.conf import settings
from kasyachnik.users.models import get_or_create_user
from kasyachnik.bot.models import get_or_create_chat, save_message
import requests
import json


class Kasyachnik:
    __instance = None

    def __init__(self):
        if not Kasyachnik.__instance:
            self.save_messages = True
            self.commands_prefix = '/'
            self.commands_list = ['banek', 'shama']
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
            if self._message_obj:
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
