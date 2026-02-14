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
    
    
