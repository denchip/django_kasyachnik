import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_id = models.UUIDField(null=True, blank=True, editable=False, db_index=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    def __str__(self):
        if self.telegram_username:
            return self.telegram_username
        else:
            return str(self.id)


def create_user_from_weebhook(request_data=None):
    from_id = request_data['message']['from']['id']
    username = request_data['message']['from'].get('username', None)
    first_name = request_data['message']['from'].get('first_name', None)
    last_name = request_data['message']['from'].get('last_name', None)
    User.objects.create(telegram_id=from_id, telegram_username=username, first_name=first_name,
                        last_name=last_name)