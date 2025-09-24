from django.db import models


class Character(models.Model):
    GENDER = (
        ('M', 'Мужской'),
        ('F', 'Женский'),
    )
        
    name = models.CharField('Имя модели', max_length=20)

    gender = models.CharField(
        max_length=1,
        choices=GENDER,
        default='F',
        verbose_name="Пол"
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Персонаж'
        verbose_name_plural = 'Персонажи'
    
    
