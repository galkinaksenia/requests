from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pytest
from django.urls import reverse
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

#Функциональные тесты
@pytest.fixture(scope='function')
def driver():
    # Инициализация веб-драйвера
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Запуск в фоновом режиме
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


@pytest.fixture
def logistics_user(db):
    user = get_user_model().objects.create_user(username='logistics', password='password')
    user.user_type = 'logistics'
    user.save()
    return user


@pytest.fixture
def create_request(logistics_user):
    return Request.objects.create(
        cargo_type='Type A',
        origin='City A',
        destination='City B',
        driver='Driver 1',
        status='Pending',
        created_by=logistics_user
    )


def test_create_request_form(driver, logistics_user):
    driver.get(reverse('create_request'))
    driver.find_element(By.NAME, 'cargo_type').send_keys('Type B')
    driver.find_element(By.NAME, 'origin').send_keys('City C')
    driver.find_element(By.NAME, 'destination').send_keys('City D')
    driver.find_element(By.NAME, 'driver').send_keys('Driver 2')

    # Отправка формы
    driver.find_element(By.XPATH, "//button[contains(text(),'Создать заявку')]").click()

    # Проверка редиректа и наличия заявки
    assert 'dashboard' in driver.current_url
    assert 'Type B' in driver.page_source


def test_update_request_status_form(driver, logistics_user, create_request):
    driver.get(reverse('update_request_status', args=[create_request.id]))
    driver.find_element(By.NAME, 'status').send_keys('Approved')

    # Отправка формы
    driver.find_element(By.XPATH, "//button[contains(text(),'Сохранить изменения')]").click()

    # Проверка редиректа и изменения статуса
    assert 'dashboard' in driver.current_url
    assert 'Approved' in driver.page_source

#Нагрузочные тесты
@pytest.fixture(scope='function')
def driver():
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

def test_performance_load_dashboard(driver):
    start_time = time.time()
    driver.get(reverse('dashboard'))  # Замените на фактический URL
    duration = time.time() - start_time
    assert duration < 2  # Проверка, что загрузка страницы занимает менее 2 секунд


#Тестирование пользовательского интерфейса (UI)
@pytest.fixture(scope='function')
def driver():
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

def test_ui_elements_on_dashboard(driver, logistics_user):
    driver.get(reverse('dashboard'))
    driver.find_element(By.XPATH, "//h1[contains(text(),'Dashboard')]")  # Проверка заголовка
    assert driver.find_element(By.ID, 'create-request-button').is_displayed()  # Проверка наличия кнопки создания заявки
    assert driver.find_element(By.CLASS_NAME, 'request-list').is_displayed()  # Проверка наличия списка заявок

def test_ui_responsiveness(driver):
    driver.set_window_size(375, 667)  # Размер экрана для мобильных устройств
    driver.get(reverse('dashboard'))
    assert driver.find_element(By.XPATH, "//button[contains(text(),'Создать заявку')]").is_displayed()  # Проверка наличия кнопки на мобильном экране

    driver.set_window_size(1024, 768)  # Размер экрана для планшетов
    driver.get(reverse('dashboard'))
    assert driver.find_element(By.XPATH, "//button[contains(text(),'Создать заявку')]").is_displayed()  # Проверка наличия кнопки на планшете


#Тестирование пользовательского опыта (UX)

@pytest.fixture(scope='function')
def driver():
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def test_tooltips_and_help_text(driver, logistics_user):
    driver.get(reverse('create_request'))
    cargo_type_input = driver.find_element(By.NAME, 'cargo_type')
    cargo_type_input.click()
    assert driver.find_element(By.XPATH, "//div[@class='tooltip']").is_displayed()  # Проверка наличия подсказки


def test_error_messages_on_invalid_input(driver, logistics_user):
    driver.get(reverse('create_request'))
    driver.find_element(By.NAME, 'cargo_type').send_keys('')  # Пустое поле
    driver.find_element(By.XPATH, "//button[contains(text(),'Создать заявку')]").click()

    assert driver.find_element(By.XPATH,
                               "//div[contains(text(),'Это поле обязательно для заполнения')]").is_displayed()  # Проверка сообщения об ошибке
