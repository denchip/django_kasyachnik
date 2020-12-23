from django.db import models
from kasyachnik.users.models import User
from kasyachnik.bot.enums import BetsStatus


class Chat(models.Model):
    telegram_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='user_chats')

    def __str__(self):
        return self.title or self.id


def get_or_create_chat(message=None):
    if message['chat']['type'] == 'private':
        return None

    chat_id = message['chat']['id']
    chat = Chat.objects.filter(telegram_id=chat_id).first()
    if not chat:
        chat = Chat.objects.create(telegram_id=chat_id, title=message['chat']['title'])
    return chat


class Message(models.Model):
    telegram_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    chat = models.ForeignKey(Chat, related_name='chat_messages', null=True, blank=True, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='user_messages', null=True, blank=True, on_delete=models.CASCADE)
    text = models.CharField(max_length=1023, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    edited = models.DateTimeField(auto_now=True, editable=False)


def save_message(user=None, chat=None, message=None):
    message_id = message['message_id']
    if 'text' in message:
        message_obj = Message.objects.filter(telegram_id=message_id).first()
        if not message_obj:
            if chat:
                message_obj = Message.objects.create(telegram_id=message_id, chat=chat, sender=user,
                                                     text=message['text'])
            else:
                message_obj = Message.objects.create(telegram_id=message_id, sender=user, text=message['text'])
        else:
            message_obj.text = message['text']
            message_obj.save()
        return message_obj


class Bets(models.Model):
    title = models.CharField(max_length=1023)
    initiator = models.ForeignKey(User, related_name='user_started_bets', null=True, blank=True,
                                  on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, related_name='chat_started_bets', null=True, blank=True,
                             on_delete=models.CASCADE)
    status = models.CharField(max_length=1023, choices=BetsStatus.choices(), default=BetsStatus.OPENED.value)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    edited = models.DateTimeField(auto_now=True, editable=False)


class BetsOption(models.Model):
    number = models.IntegerField()
    bets = models.ForeignKey(Bets, related_name='options', null=True, blank=True,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=1023)

    def __str__(self):
        return self.title


class Bet(models.Model):
    bets = models.ForeignKey(BetsOption, related_name='bets_obj', null=True, blank=True,
                             on_delete=models.CASCADE)
    bettor = models.ForeignKey(User, related_name='user_bets', null=True, blank=True,
                               on_delete=models.CASCADE)
    amount = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
    edited = models.DateTimeField(auto_now=True, editable=False)
