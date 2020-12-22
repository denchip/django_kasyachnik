from django.contrib import admin
from kasyachnik.bot.models import Message, Chat


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'text', 'created', 'edited']
    ordering = ['-created', '-edited']
