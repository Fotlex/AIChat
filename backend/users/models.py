from django.db import models

class User(models.Model):
    id = models.BigIntegerField('Идентификатор Телеграм', primary_key=True, blank=False)
    
    username = models.CharField('Юзернейм', max_length=64, null=True, blank=True)
    first_name = models.CharField('Имя', null=True, blank=True)
    last_name = models.CharField('Фамилия', null=True, blank=True)

    balance = models.IntegerField('Баланс', default=0)
    
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True, blank=True)
    
    
    def __str__(self):
        return f'id{self.id} | @{self.username or "-"} {self.first_name or "-"} {self.last_name or "-"}'

    class Meta:
        verbose_name = 'Телеграм пользователь'
        verbose_name_plural = 'Телеграм пользователи'
