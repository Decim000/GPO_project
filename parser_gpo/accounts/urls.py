from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts import views
from accounts.views import ProfileViewSet

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    #Регистрация
    #http://127.0.0.1:8000/auth/users/

    #Подтверждение почты
    #http://127.0.0.1:8000/auth/users/activation/

    #Вход по JWT
    #http://127.0.0.1:8000/auth/jwt/create/

    #Обновление токена
    #http://127.0.0.1:8000/auth/jwt/refresh/

    #Email для смены пароля
    #http://127.0.0.1:8000/auth/users/reset_password/

    #Смена пароля по токену из Email
    #http://127.0.0.1:8000/auth/users/reset_password_confirm/
]
