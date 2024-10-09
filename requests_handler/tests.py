import time
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Request

import unittest
from django.test import Client
from django.urls import reverse
from .models import CustomUser, Request

# Функциональные тесты
@pytest.fixture
def logistics_user(db):
    user = get_user_model().objects.create_user(username='logistics', password='password')
    user.user_type = 'logistics'
    user.save()
    return user

@pytest.fixture
def accountant_user(db):
    user = get_user_model().objects.create_user(username='accountant', password='password')
    user.user_type = 'accountant'
    user.save()
    return user

@pytest.fixture
def create_request(logistics_user):
    return Request.objects.create(
        customer_name = 'ООО "СтройМастер"',
        driver_name = 'Сидоров',
        cargo = 'Доски',
        direction = 'Москва',
        cost = 50000,
        vehicle = 'DAF A100AA 152',
        trailer = 'A200AA 252',
        logistics_person = 4
    )

def test_create_request(client):
    client.login(username='logistics', password='password')
    response = client.post(reverse('create_request'), {
        'customer_name': 'ООО "СтройМастер"',
        'driver_name': 'Сидоров',
        'cargo': 'Доски',
        'direction': 'Москва',
        'cost': 50000,
        'vehicle': 'DAF A100AA 152',
        'trailer': 'A200AA 252',
        'logistics_person': 4
    })
    assert response.status_code == 302  # Redirect after successful submission
    assert Request.objects.filter(cargo_type='Type B').exists()

def test_update_request_status(client, accountant_user, create_request):
    client.login(username='accountant', password='password')
    request_id = create_request.id
    response = client.post(reverse('update_request_status', args=[request_id]), {
        'status': 'paid'
    })
    assert response.status_code == 302  # Redirect after successful update
    request_obj = Request.objects.get(id=request_id)
    assert request_obj.status == 'paid'

def test_delete_request(client, create_request):
    client.login(username='employee', password='password')
    request_id = create_request.id
    response = client.post(reverse('delete_request', args=[request_id]))  # Предполагается, что такой URL существует

    assert response.status_code == 302  # Redirect after successful deletion
    assert not Request.objects.filter(id=request_id).exists()

def test_search_requests(client):
    client.login(username='logistics', password='password')
    response = client.get(reverse('dashboard'), {'search': 'Сидоров'})
    assert response.status_code == 200
    assert 'Сидоров' in str(response.content)

# Нагрузочные тесты
@pytest.mark.django_db
def test_performance_create_requests(client, logistics_user):
    client.login(username='logistics', password='password')
    start_time = time.time()

    for _ in range(1000):  # Создаем 1000 заявок
        client.post(reverse('create_request'), {
            'customer_name': 'ООО "СтройМастер"',
            'driver_name': 'Сидоров',
            'cargo': 'Доски',
            'direction': 'Москва',
            'cost': 50000,
            'vehicle': 'DAF A100AA 152',
            'trailer': 'A200AA 252',
            'logistics_person': 4
        })

    duration = time.time() - start_time
    assert duration < 5  # Проверяем, что время выполнения не больше 5 секунд


# Интеграционные тесты
@pytest.mark.django_db
def test_database_operations(create_request):
    # Чтение
    request_obj = Request.objects.get(id=create_request.id)
    assert request_obj.cargo == 'Доски'

    # Обновление
    create_request.status = 'new'
    create_request.save()
    assert create_request.status == 'new'

    # Удаление
    request_id = create_request.id
    create_request.delete()
    assert not Request.objects.filter(id=request_id).exists()

# Регрессионные тесты
@pytest.mark.django_db
def test_existing_functionality(client, logistics_user):
    # Тестирование создания и поиска
    client.login(username='logistics', password='password')
    response = client.post(reverse('create_request'), {
        'customer_name': 'ООО "СтройМастер"',
        'driver_name': 'Сидоров',
        'cargo': 'Доски',
        'direction': 'Москва',
        'cost': 50000,
        'vehicle': 'DAF A100AA 152',
        'trailer': 'A200AA 252',
        'logistics_person': 4
    })
    assert response.status_code == 302  # Redirection after creation
    assert Request.objects.filter(cargo='Доски').exists()


class DashboardTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.logistics_user = CustomUser.objects.create_user(username='logistics_user', password='test_password', user_type='logistics')
        self.accountant_user = CustomUser.objects.create_user(username='accountant_user', password='test_password', user_type='accountant')
        self.request = Request.objects.create()

    def test_dashboard(self):
        # Логист
        self.client.force_login(self.logistics_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('can_create' in response.context)
        self.assertTrue(response.context['can_create'])

        # Бухгалтер
        self.client.force_login(self.accountant_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('can_edit_status' in response.context)
        self.assertTrue(response.context['can_edit_status'])

        # Без роли
        self.client.force_login(CustomUser.objects.create_user(username='non_role_user', password='test_password'))
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse('can_create' in response.context)
        self.assertFalse('can_edit_status' in response.context)