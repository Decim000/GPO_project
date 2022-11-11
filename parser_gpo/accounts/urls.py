from django.contrib import admin
from django.urls import path, include

urlpatterns = [
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
