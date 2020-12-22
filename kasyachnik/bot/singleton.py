from django.conf import settings
import requests


class Kasyachnik:
    __instance = None

    def __init__(self):
        if not Kasyachnik.__instance:
            pass
        else:
            self.get_instance()

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Kasyachnik()
        return cls.__instance

    @staticmethod
    def send_message(message, chat_id, parse_mode="Markdown"):
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
        }
        response = requests.post(
            f"{settings.TELEGRAM_URL}{settings.TELEGRAM_BOT_TOKEN}/sendMessage", data=data
        )
        return response


bot = Kasyachnik.get_instance()
