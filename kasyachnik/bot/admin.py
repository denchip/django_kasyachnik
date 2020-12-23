from django.contrib import admin
from kasyachnik.bot.models import Message, Chat, Bets, BetsOption, Bet


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'text', 'created', 'edited']
    ordering = ['-edited', '-created']


@admin.register(Bets)
class BetsAdmin(admin.ModelAdmin):
    pass


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['bettor', 'amount', 'bets']


@admin.register(BetsOption)
class BetsOptionAdmin(admin.ModelAdmin):
    pass
