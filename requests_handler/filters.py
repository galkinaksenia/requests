import django_filters
from .models import Request
from django_filters import DateFilter
from django.forms.widgets import DateInput

class RequestFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(field_name='customer_name', label="Заказчик", lookup_expr='icontains')
    driver_name = django_filters.CharFilter(field_name='driver_name', label="Водитель", lookup_expr='icontains')
    cargo = django_filters.CharFilter(field_name='cargo', label="Груз", lookup_expr='icontains')
    direction = django_filters.CharFilter(field_name='direction', label="Направление", lookup_expr='icontains')
    status = django_filters.ChoiceFilter(field_name='status', label="Статус", choices=Request.STATUS_CHOICES)
    created_at = django_filters.DateFilter(field_name='created_at', label="Дата создания", lookup_expr='icontains',
                                           widget=DateInput(attrs={'type': 'date'}))
    created_at_gte = DateFilter(field_name='created_at', label='Дата начала', lookup_expr='gte',
                                widget=DateInput(attrs={'type': 'date'}))
    created_at_lte = DateFilter(field_name='created_at', label='Дата окончания', lookup_expr='lte',
                                widget=DateInput(attrs={'type': 'date'}))
    cost = django_filters.CharFilter(field_name='cost', label="Стоимость", lookup_expr='icontains')
    cost_gt = django_filters.NumberFilter(field_name='cost', label="Стоимость больше чем", lookup_expr='gt')
    cost_lt = django_filters.NumberFilter(field_name='cost', label="Стоимость меньше чем", lookup_expr='lt')
    vehicle = django_filters.CharFilter(label="Транспортное средство", lookup_expr='icontains')
    trailer = django_filters.CharFilter(label="Прицеп", lookup_expr='icontains')

    class Meta:
        model = Request
        fields = [
            'customer_name',
            'driver_name',
            'cargo',
            'direction',
            'status',
            'created_at',
            'created_at_gte',
            'created_at_lte',
            'cost',
            'cost_gt',
            'cost_lt',
            'vehicle',
            'trailer'
        ]