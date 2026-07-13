from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Добро пожаловать в API!</h1><p>Доступные эндпоинты:</p><ul><li><a href='/api/courses/'>/api/courses/</a></li><li><a href='/api/lessons/'>/api/lessons/</a></li></ul>")

urlpatterns = [
    path('', home),  # Добавляем корневой путь
    path('admin/', admin.site.urls),
    path('api/', include('materials.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)