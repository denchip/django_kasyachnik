import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_id = models.CharField(max_length=255, null=True, blank=True, editable=False, db_index=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    def __str__(self):
        if self.telegram_username:
            return self.telegram_username
        else:
            return str(self.id)


def get_or_create_user(message=None):
    from_id = message['from']['id']
    user = User.objects.filter(telegram_id=from_id).first()
    if not user:
        username = message['from'].get('username', None)
        first_name = message['from'].get('first_name', "")
        last_name = message['from'].get('last_name', "")
        user = User.objects.create(telegram_id=from_id, telegram_username=username, first_name=first_name,
                                   last_name=last_name, username=from_id)
    return user
