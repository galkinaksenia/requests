from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Request, CustomUser, Feedback

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['customer_name', 'driver_name', 'cargo', 'direction', 'cost', 'vehicle', 'trailer', 'additional_info']

        labels = {
            'customer_name': 'Заказчик',
            'driver_name': 'Водитель',
            'cargo': 'Груз',
            'direction': 'Направление',
            'cost': 'Стоимость',
            'vehicle': 'Машина',
            'trailer': 'Прицеп',
            'additional_info': 'Дополнительная информация',
        }

# Добавляем форму для обновления статуса
class UpdateRequestStatusForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['status']
        labels = {
            'status': 'Статус',
        }

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'user_type']
        user_type = forms.ChoiceField(choices=CustomUser.USER_TYPES, widget=forms.RadioSelect, required=True)
        labels = {
            'user_type': 'Тип пользователя'
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваше сообщение'}),
        }
        labels = {
            'message': 'Сообщение'
        }