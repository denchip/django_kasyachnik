from django.conf import settings
from django.urls import include, path, re_path, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.views.decorators.csrf import csrf_exempt
from kasyachnik.bot.views import WebHookView
from kasyachnik.users.views import LoginView, BetsView

urlpatterns = [
    path('', LoginView.as_view()),
    path('admin/', admin.site.urls),
    path('auth/complete/telegram/', BetsView.as_view()),
    path(f'webhook/{settings.TELEGRAM_BOT_TOKEN}/', csrf_exempt(WebHookView.as_view())),

    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
