import os
import uuid

from django.db import models


def tariff_photo_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"

    return f"tariff/{new_filename}"

class Tariff(models.Model):
    name = models.CharField('Наименование тарифа')
    cost = models.PositiveIntegerField('Цена в рублях')
    reward = models.PositiveIntegerField('Количество валюты')
    
    photo = models.ImageField("Фото тарифа", upload_to=tariff_photo_path, blank=True, null=True)
    
    
    def __str__(self):
        return f'{self.name} | {self.cost} руб'

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        
        
class Payment(models.Model):
    STATUS = (
        ('pending', 'Ожидание'),
        ('canceled', 'Отменен'),
        ('succeeded', 'Успешный')
    )
    payment_id = models.CharField(
        max_length=36,  
        unique=True,    
        verbose_name="ID платежа в ЮKassa"
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Тариф",
    )
    
    status = models.CharField(choices=STATUS, default='pending', verbose_name='Статус платежа')
    create_at = models.DateTimeField(auto_created=True, verbose_name='Дата создания платежа')
    
    def __str__(self):
        return f"Пользователь {self.user.id}"
    
    
    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
    
    
