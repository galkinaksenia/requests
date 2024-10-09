import base64
import qrcode
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum
from django_otp.plugins.otp_totp.models import TOTPDevice
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .forms import RequestForm, UpdateRequestStatusForm, UserRegistrationForm
from .models import Request, ErrorLog, CustomUser, Feedback
from .filters import RequestFilter
from .forms import FeedbackForm

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Если пользователь аутентифицирован, перенаправляем на страницу ввода кода
            if user.devices.exists():  # Проверяем, есть ли у пользователя устройство MFA
                request.session['username'] = username
                return redirect('otp_login')  # URL для ввода кода MFA
            else:
                login(request, user)
                return redirect('dashboard')
        else:
            ErrorLog.objects.create(message='Неуспешная попытка входа', status='Необработанная')
            messages.error(request, "Неправильное имя пользователя или пароль.")
    return render(request, 'login.html')

@login_required
def dashboard_view(request):
    can_create = False
    can_edit_status = False
    if is_logistics(request.user):
        requests = Request.objects.filter(logistics_person=request.user)
        #requests = Request.objects.all()
        sort_by = request.GET.get('sort', 'id')  # По умолчанию сортируем по ID
        if sort_by in ['id', 'customer_name', 'driver_name', 'cargo', 'direction', 'cost', 'vehicle', 'trailer',
                       'additional_info', 'status']:
            requests = requests.order_by(sort_by)  # Сортируем заявки по указанному полю
        can_create = True
    elif is_accountant(request.user):
        requests = Request.objects.all()
        sort_by = request.GET.get('sort', 'id')  # По умолчанию сортируем по ID
        if sort_by in ['id', 'customer_name', 'driver_name', 'cargo', 'direction', 'cost', 'vehicle', 'trailer',
                       'additional_info', 'status']:
            requests = requests.order_by(sort_by)  # Сортируем заявки по указанному полю
        can_edit_status = True

    elif is_employee(request.user):
        return redirect('admin')
    else:
        requests = Request.objects.none()  # Если у пользователя нет роли

    request_filter = RequestFilter(request.GET, queryset=requests)
    requests = request_filter.qs

    return render(request, 'dashboard.html', {
            'requests': requests,
            'filter': request_filter,
            'can_create': can_create,
            'can_edit_status': can_edit_status,
        })


# Проверяем, является ли пользователь логистом
def is_logistics(user):
    return user.user_type == 'logistics'


# Проверяем, является ли пользователь бухгалтером
def is_accountant(user):
    return user.user_type == 'accountant'


# Проверяем, является ли пользователь сотрудником
def is_employee(user):
    return user.user_type == 'employee'


# Доступ только для логистов
@login_required
@user_passes_test(is_logistics)
def create_request_view(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.logistics_person = request.user  # Сохранение пользователя
            new_request.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('dashboard')
    else:
        form = RequestForm()

    return render(request, 'create_request.html', {'form': form})


# Доступ только для бухгалтеров
@login_required
@user_passes_test(is_accountant)
def update_request_status_view(request):
    form = None
    request_obj = None
    if request.method == 'GET':
        request_id = request.GET.get('request_id')
        try:
            request_obj = Request.objects.get(id=request_id)
            form = UpdateRequestStatusForm(instance=request_obj)
        except Request.DoesNotExist:
            ErrorLog.objects.create(message='Заявка не найдена!', status='Необработанная')
            messages.error(request, 'Заявка не найдена!')
            return redirect('dashboard')
    elif request.method == 'POST':
        request_id = request.POST.get('id')  # Получаем ID из POST-запроса
        try:
            request_obj = Request.objects.get(id=request_id)
            form = UpdateRequestStatusForm(request.POST, instance=request_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Статус заявки успешно обновлён!')
                return redirect('dashboard')
        except Request.DoesNotExist:
            ErrorLog.objects.create(message='Заявка не найдена!', status='Необработанная')
            messages.error(request, 'Заявка не найдена!')

    return render(request, 'update_request_status.html', {'form': form, 'request': request_obj})


@login_required
def profile_view(request):
    # Получение логиста и его заявок
    requests = Request.objects.filter(logistics_person=request.user)
    feedback_sent = False  # Переменная для отслеживания отправки обратной связи

    # Обработка обратной связи
    if request.method == 'POST':
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            feedback = feedback_form.save(commit=False)
            feedback.user = request.user  # Ассоциируем сообщение с пользователем
            feedback.save()
            feedback_sent = True  # Устанавливаем, что сообщение успешно отправлено
    else:
        feedback_form = FeedbackForm()

    context = {
        'user': request.user,
        'requests': requests,
        'feedback_form': feedback_form,
        'feedback_sent': feedback_sent,  # Передаем информацию в шаблон
    }
    return render(request, 'profile.html', context)


@login_required
def admin_view(request):
    active_requests_count = Request.objects.filter(status='new').count()
    registered_users_count = CustomUser.objects.count()
    error_logs = ErrorLog.objects.all()  # Получение всех записей в журнале ошибок
    feedbacks = Feedback.objects.all()  # Получение всех обратной связи

    context = {
        'active_requests_count': active_requests_count,
        'registered_users_count': registered_users_count,
        'error_logs': error_logs,
        'feedbacks': feedbacks
    }
    return render(request, 'admin.html', context)


@login_required
@user_passes_test(is_employee)
def delete_request_by_id(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        try:
            request_to_delete = get_object_or_404(Request, id=request_id)
            request_to_delete.delete()
            messages.success(request, f"Заявка с ID {request_id} была успешно удалена.")
        except Exception as e:
            messages.error(request, f"Ошибка удаления заявки: {str(e)}")
            ErrorLog.objects.create(message="Ошибка удаления заявки", status='Необработанная')
    return redirect('admin')


@login_required
@user_passes_test(is_employee)
def delete_user_by_id(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user_to_delete = get_object_or_404(CustomUser, id=user_id)
            if user_to_delete.is_superuser:
                messages.error(request, "Нельзя удалить суперпользователя.")
                ErrorLog.objects.create(message="Попытка удалить суперпользователя", status='Необработанная')
            else:
                user_to_delete.delete()
                messages.success(request, f"Пользователь с ID {user_id} был успешно удалён.")
        except Exception as e:
            messages.error(request, f"Ошибка удаления пользователя: {str(e)}")
            ErrorLog.objects.create(message="Ошибка удаления пользователя", status='Необработанная')
    return redirect('admin')

@login_required
@user_passes_test(is_employee)
def mark_feedback_as_read(request, feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)
    feedback.is_read = True
    feedback.save()
    return redirect('admin')


@login_required
@user_passes_test(is_employee)
def mark_error_as_read(request, error_id):
    error_log = get_object_or_404(ErrorLog, id=error_id)
    error_log.is_read = True
    error_log.save()
    return redirect('admin')

@login_required
def report_view(request):
    total_requests = Request.objects.count()
    total_cost = Request.objects.aggregate(Sum('cost'))['cost__sum']

    # Подсчет заявок по статусу
    request_status_stats = Request.objects.values('status').annotate(request_count=Count('id'))

    # Подсчет популярных направлений
    popular_directions = Request.objects.values('direction').annotate(direction_count=Count('id')).order_by(
        '-direction_count')[:5]

    # Создаем графики
    fig, ax = plt.subplots(figsize=(10, 6))

    # График по статусам заявок
    statuses = [stat['status'] for stat in request_status_stats]

    for i, status in enumerate(statuses):
        if status == 'new':
            statuses[i] = 'Новая'
        elif status == 'paid':
            statuses[i] = 'Оплачена'
        else:
            statuses[i] = 'Отменена'

    request_counts = [stat['request_count'] for stat in request_status_stats]

    ax.bar(statuses, request_counts, color='blue')
    ax.set_title('Количество заявок по статусам')
    ax.set_xlabel('Статусы')
    ax.set_ylabel('Количество заявок')
    plt.xticks(rotation=45)

    # Сохранение графика в объект BytesIO и преобразование в base64
    buffer = BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    img = buffer.getvalue()
    img_b64 = base64.b64encode(img).decode('utf-8')  # Кодируем в base64 строку

    context = {
        'total_requests': total_requests,
        'total_cost': total_cost,
        'request_status_stats': request_status_stats,
        'popular_directions': popular_directions,
        'status_chart': img_b64,  # передаем изображение диаграммы в контекст
    }
    return render(request, 'report.html', context)


def otp_login_view(request):
    username = request.session.get('username')
    user = authenticate(username=username)

    if request.method == 'POST':
        token = request.POST.get('token')
        try:
            device = TOTPDevice.objects.get(user=user)
            if device.verify_token(token):
                login(request, user)
                del request.session['username']  # Удаляем временную сессию
                return redirect('dashboard')
            else:
                messages.error(request, "Неверный код.")
        except TOTPDevice.DoesNotExist:
            messages.error(request, "Устройство не найдено.")

    return render(request, 'otp_login.html')

@login_required
def add_otp_device(request):
    user = request.user
    if request.method == 'POST':
        # Создаем новое TOTP устройство
        device = TOTPDevice.objects.create(user=user, name='Default TOTP Device')
        return redirect('otp_device_qr', device_id=device.id)

    return render(request, 'add_device.html')


@login_required
def otp_device_qr(request, device_id):
    device = TOTPDevice.objects.get(id=device_id)
    uri = device.config_url  # Получаем URL конфигурации
    img = qrcode.make(uri)

    # Сохраните QR-код в памяти
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'show_qr_code.html', {'image': f'data:image/png;base64,{img_str}'})