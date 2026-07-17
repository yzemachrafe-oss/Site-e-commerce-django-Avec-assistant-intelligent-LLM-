from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop import views  # 🔥 هاهي زدناها هنا باش تـفيكسا الـ NameError

urlpatterns = [
    # 🤖 حطيناه هو الأول باش يخدم ديريكت فـ /assistant/
    path('assistant/', views.chatbot_view, name='assistant'),

    path('django-admin/', admin.site.urls),
    path('', include('shop.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)