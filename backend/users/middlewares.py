import datetime
import os
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone

from rest_framework import status

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.errors import InvalidInitDataError

from .models import User


class TWAAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._telegram_authenticator = TelegramAuthenticator(settings.TELEGRAM_SECRET_KEY)
        
    def __call__(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)
            
        auth_cred = request.headers.get('Telegram-Init-Data')
        
        if not auth_cred:
            return JsonResponse(
                data={'error': 'Authorization header required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            init_data = self._telegram_authenticator.validate(auth_cred)
            print("correct init data")
        except InvalidInitDataError:
            print("invalid init data")
            return JsonResponse(
                data={'error': 'Invalid Telegram auth data'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            current_user = User.objects.filter(telegram_id=init_data.user.id).first()
            print("start_param:", init_data.start_param)
            if not current_user:    
                print("create_user")

                current_user = User.objects.create(
                    telegram_id=init_data.user.id,
                    username=init_data.user.username,
                    first_name=init_data.user.first_name,
                    last_name=init_data.user.last_name,
                )
                
                current_user.save()
            
            request.tg_user = current_user
            return self.get_response(request)
        except Exception as e:
            print('error:', str(e))
            return JsonResponse(
                data={'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )