from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django_otp.plugins.otp_totp.models import TOTPDevice

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('employee', 'Сотрудник платформы'),
        ('logistics', 'Логист'),
        ('accountant', 'Бухгалтер'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='employee', blank=False)
    devices = models.ManyToManyField(TOTPDevice)

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Связь с пользователем
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class ErrorLog(models.Model):
    message = models.TextField()  # Описание ошибки
    timestamp = models.DateTimeField(default=timezone.now)  # Время возникновения ошибки
    status = models.CharField(max_length=20, default='Неисправность')  # Статус ошибки
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.timestamp}: {self.message} ({self.status})"


class Request(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('paid', 'Оплачена'),
        ('canceled', 'Отменена'),
    ]

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new', blank=False)
    customer_name = models.CharField(max_length=100, blank=False)
    driver_name = models.CharField(max_length=100, blank=False)
    cargo = models.CharField(max_length=100, blank=False)
    direction = models.CharField(max_length=200, blank=False)
    cost = models.DecimalField(max_digits=50, decimal_places=2, blank=False)
    vehicle = models.CharField(max_length=100, blank=False)
    trailer = models.CharField(max_length=100, blank=False)
    additional_info = models.TextField(blank=True, null=True)
    logistics_person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Request {self.id} from {self.customer_name} - Status: {self.status}"