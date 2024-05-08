import json
import datetime
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import render, redirect
from collections import defaultdict
from .forms import *
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.cache import cache_page


def generate_reset_password_link(request, user, mail):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = reverse('travel_site:password_reset', kwargs={'uidb64': uidb64, 'token': token, 'mail': mail})
    # Добавляем 30 минут к текущему времени
    expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
    # Создаем запись во временном хранилище (session) для этой ссылки с установленным временем жизни
    request.session[f'reset_password_link_{mail}'] = {'url': reset_url, 'expiration_time': str(expiration_time)}
    return request.build_absolute_uri(reset_url)


def generate_email_activate_link(request, user, mail, phone):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    active_url = reverse('travel_site:email_activate', kwargs={'uidb64': uidb64, 'token': token, 'mail': mail})
    # Добавляем 30 минут к текущему времени
    expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
    # Создаем запись во временном хранилище (session) для этой ссылки с установленным временем жизни
    request.session[f'activate_email_link_{mail}'] = {'url': active_url, 'phone': phone, 'expiration_time': str(expiration_time)}
    return request.build_absolute_uri(active_url)


def forms(request, context):
    if request.method == 'POST':
        register_form = UserRegisterForm(request.POST)  # создаем форму на основен пришедших данных
        login_form = UserLoginForm(data=request.POST)  # создаем форму на основен пришедших данных
        password_forget_form = PasswordForgetUserForm(request.POST)  # создаем форму на основен пришедших данных
        if register_form.is_valid():  # если эта форма валидна
            user = register_form.save()  # сохраняем пользователя
            user.is_active = False  # ставим ему неактивный, ибо он не подтвердил почту
            reset_link = generate_email_activate_link(request, user, user.email, user.username)
            user.username = user.pk  # ставлю на время номер как id
            user.phone = user.pk
            send_mail('Treva. Подтверждение почты',
                      f'Перейдите по ссылке для подтверждения почты: {reset_link}',
                      'trevatours@yandex.ru',
                      [user.email, ],
                      fail_silently=False, )  # отправляем почту
            messages.success(request,
                             '<span>Готово!</span> Для окончания регистрации пройдите по ссылке на указанной при регистрации почте.')
            user.save()
        # else:
        #     if request.POST.get('phone', False):
        #         user = User.objects.filter(username=request.POST['phone']).first()
        #         if user:
        #             try:
        #                 date_string = request.session[f'activate_email_link_{request.POST["email"]}']['expiration_time']
        #                 formatted_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
        #                 if formatted_date < datetime.datetime.now():
        #                     del request.session[f'activate_email_link_{request.POST["email"]}']
        #                     user.delete()
        #                     request.session.modified = True
        #                 user.save()  # сохраняем пользователя
        #                 user.is_active = False  # ставим ему неактивный, ибо он не подтвердил почту
        #                 reset_link = generate_email_activate_link(request, user, user.email, user.username)
        #                 user.username = user.pk  # ставлю на время номер как id
        #                 user.phone = user.pk
        #                 send_mail('Treva. Подтверждение почты',
        #                           f'Перейдите по ссылке для подтверждения почты: {reset_link}',
        #                           'trevatours@yandex.ru',
        #                           [user.email, ],
        #                           fail_silently=False, )  # отправляем почту
        #                 messages.success(request,
        #                                  '<span>Готово!</span> Для окончания регистрации пройдите по ссылке на указанной при регистрации почте.')
        #                 user.save()
        #             except KeyError:
        #                 pass

        if login_form.is_valid():  # если эта форма валидна
            data = request.POST['data']  # поле где можно вписать номер, имя или почту
            password = request.POST['password']  # поле с паролем
            users = User.objects.filter(first_name=data)  # находим по имени всех пользователей
            user1 = None
            for user in users:
                if (check_password(password, user.password) or password == user.password) and user.is_active:  # проверяем пароль, который пришел, и пароль пользователя которого нашли по имени
                    user1 = user  # присваиваем вместо None
            if user1:
                request.session.pop('cart_auth', None)
                login(request, user1)   # Авторизуем пользователя
                return "Login"
            phone = request.POST['data']  # получаем в переменную то что он ввёл (телефон)
            phone_first_char = request.POST['data'][:1]  # получаем первый символ (у телефона это 7)
            if '@' not in phone and phone_first_char == '7':  # если в том, что он ввёл нет собачки, и первый символ это 7 а не например +, то добавим плюс чтобы в базе нашелся такой пользователь ибо в базе он с плюсом номер
                phone = '+' + phone
            user2 = User.objects.filter(username=phone).first()  # находим по телефону
            if user2:  # проверяем пароль
                if user2.is_active and (check_password(password, user2.password) or password == user2.password):
                    request.session.pop('cart_auth', None)
                    login(request, user2)  # Авторизуем пользователя
                    return "Login"
            user3 = User.objects.filter(email=data).first()  # находим по почте
            if user3:  # проверяем пароль
                if user3.is_active and (check_password(password, user3.password) or password == user3.password):
                    request.session.pop('cart_auth', None)
                    login(request, user3)  # Авторизуем пользователя
                    return "Login"
            login_form.add_error(None, 'Пользователь не найден')

        if password_forget_form.is_valid():  # если эта форма валидна
            forget = request.POST['forget']  # поле с почтой
            user = User.objects.filter(email=forget).first()  # находим пользователя по введённой почте
            if user:
                reset_link = generate_reset_password_link(request, user, forget)
                send_mail(
                    'Treva. Сброс пароля',
                    f'Сброс пароля по электронной почте. Перейдите по ссылке для переопределения пароля: {reset_link}',
                    'trevatours@yandex.ru',
                    [forget, ],
                    fail_silently=False,
                )
                messages.success(request, 'Проверьте вашу почту. ')
            else:
                password_forget_form.add_error(None, 'Электронная почта не найдена')
    else:
        register_form = UserRegisterForm()  # просто форма при просто странице
        login_form = UserLoginForm()  # просто форма при просто странице
        password_forget_form = PasswordForgetUserForm()  # просто форма при просто странице
    context['register_form'] = register_form
    context['login_form'] = login_form
    context['password_forget_form'] = password_forget_form


def update_available_seats(tour_id, operation, count):
    if count <= 5:
        tour = Tour.objects.get(id=tour_id)
        if operation == 'plus':
            tour.available_seats -= 1
        elif operation == 'minus':
            tour.available_seats += 1
        elif operation == 'delete_product':
            tour.available_seats += count
        tour.save()
        return {'count': tour.available_seats, 'id': tour_id}
    return {'count': 0, 'id': 0}


def cart_init(request):
    if 'cart' not in request.session:
        request.session['cart'] = {
            'full': {
                'count': 0,
            },
            'light': {
                'count': 0,
            },
            'tours': {

            },
            'products': {

            },
            'price_cart': 0,
            'create_time': datetime.datetime.now().isoformat(),
        }  # проверяем есть ли корзина в сессии, если нет то добавляем ее



def home(request):
    header_background = True
    feedbacks = Feedback.objects.filter(is_displayed=True).order_by('-id')[:5]  # берем 5 последних отзывов у которых is_displayed=True
    questions = Question.objects.filter(is_displayed=True).order_by('id')  # берем все вопросы у которых is_displayed=True

    context = {
        'title': 'Treva',
        'feedbacks': feedbacks,
        'questions': questions,
        'header_background': header_background,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'home.html', context)


def user_logout(request):
    cart_exists = request.session.get('cart', False)
    logout(request)
    if cart_exists:
        request.session['cart'] = cart_exists
        # Если в сессии есть корзина, не удаляем ее при выходе из системы
        request.session.modified = True
    return redirect('travel_site:home')


def password_reset(request, uidb64, token, mail):
    user = User.objects.get(email=mail)
    date_string = request.session[f'reset_password_link_{mail}']['expiration_time']
    formatted_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
    if formatted_date > datetime.datetime.now():
        if request.method == 'POST':
            password_reset_form = PasswordResetUserForm(request.POST)
            if password_reset_form.is_valid():
                new_password = password_reset_form.cleaned_data['password1']
                user.set_password(new_password)  # Установка нового пароля
                user.save()
                del request.session[f'reset_password_link_{mail}']
                return redirect('travel_site:home')
        else:
            password_reset_form = PasswordResetUserForm()
    else:
        password_reset_form = False
        del request.session[f'reset_password_link_{mail}']

    request.session.modified = True
    context = {
        'title': 'Сброс пароля',
        'password_reset_form': password_reset_form,
    }

    forms(request, context)

    return render(request, 'password_reset_form.html', context)


def email_activate(request, uidb64, token, mail):

    user = User.objects.get(email=mail)  # нахожу пользователя
    date_string = request.session[f'activate_email_link_{mail}']['expiration_time']
    phone = request.session[f'activate_email_link_{mail}']['phone']
    user.username = phone
    user.phone = phone
    formatted_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
    del request.session[f'activate_email_link_{mail}']
    email_active = True
    if formatted_date > datetime.datetime.now():
        user.is_active = True  # пользователь теперь активный
        user.save()
    else:
        email_active = False
        user.delete()

    context = {
        'title': 'Подтверждение почты',
        'email_active': email_active,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'email_activate.html', context)


def question_description_fetch(request):

    question_id = json.loads(request.body.decode())['id']  # Id вопроса на который нажали
    question = Question.objects.get(id=question_id)  # находим вопрос по id
    question_description = question.description  # описание найденного вопроса

    obj = {
        'status': 'ok',
        'description': question_description,
    }

    return JsonResponse(obj)


def where_to_go(request):

    tags = Tags.objects.all()  # получаем все теги локаций
    locations = Location.objects.all()  # получаем все локации

    context = {
        'title': 'Куда съездить',
        'tags': tags,
        'locations': locations
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'where_to_go.html', context)


def where_to_go_fetch(request):

    tag_id = json.loads(request.body.decode())['id']  # Id тега на который нажали
    locations = []
    if tag_id:
        tag = Tags.objects.get(id=tag_id)  # находим тег по id

        for location in tag.location.all():  # бегаем по локациям
            location_obj = {
                'tag_id': location.tags_set.all().first().id,
                'url': location.get_absolute_url(),
                'name': location.name,
                'image': location.image.url,
                'description': location.short_description,
            }

            locations.append(location_obj)
    else:
        for location in Location.objects.all():  # бегаем по локациям
            location_obj = {
                'tag_id': location.tags_set.all().first().id,
                'url': location.get_absolute_url(),
                'name': location.name,
                'image': location.image.url,
                'description': location.short_description,
            }

            locations.append(location_obj)

    obj = {
        'status': 'ok',
        'locations': locations,
    }

    return JsonResponse(obj)



@cache_page(60 * 5)
def location_detail(request, location_detail_slug):

    location = Location.objects.get(slug=location_detail_slug)  # находим локацию по слагу
    locations = Location.objects.exclude(slug=location_detail_slug).order_by('?')[:3]  # берем случайные три локации без нынешней локации
    tours = {
        'current': [],
        'next': [],
    }
    current_time = datetime.datetime.now()  # текущее время  timezone.now
    current_month_number = current_time.month  # текущий месяц
    next_month_number = current_time.month + 1  # следующий месяц
    if next_month_number > 12:  # если был декабрь(12), то добавляя 1 будет 13, а я делаю чтобы был январь(01)
        next_month_number = 1

    for tour in Tour.objects.order_by('start_date'):  # бегаем по турам и берем в ближайшие два месяца туры
        next_month = current_time.month + 1  # следующий месяц от текущего
        if current_time.month+1 > 12:  # если был декабрь(12), то добавляя 1 будет 13, а я делаю чтобы был январь(01)
            next_month = 1
        if current_time.month == tour.start_date.month:  # если текущий месяц равен месяцу тура
            if tour.start_date.day > current_time.day:  # проверяем начало тура (день) с текущим днём
                tours['current'].append(tour)
        elif next_month == tour.start_date.month:  # если текущий месяц равен следующему месяцу тура
            tours['next'].append(tour)

    tours['current'] = tours['current'][-3:]  # берем последние три самых свежих тура
    tours['next'] = tours['next'][-3:]  # берем последние три самых свежих тура
    if (current_time.year % 4 == 0 and current_time.year % 100 != 0) or current_time.year % 400 == 0:  # проверяем, если год високосный то 29 дней в феврале, иначе 28
        february_count_days = 29
    else:
        february_count_days = 28
    months = {
        '1': ["Январь", 31],
        '2': ["Февраль", february_count_days],
        '3': ["Март", 31],
        '4': ["Апрель", 30],
        '5': ["Май", 31],
        '6': ["Июнь", 30],
        '7': ["Июль", 31],
        '8': ["Август", 31],
        '9': ["Сентябрь", 30],
        '10': ["Октябрь", 31],
        '11': ["Ноябрь", 30],
        '12': ["Декабрь", 31],
    }
    current_month_name = months[str(current_month_number)]  # находим название месяца по его номеру
    next_month_name = months[str(next_month_number)]  # находим название месяца по его номеру

    context = {
        'title': location.name,
        'location': location,
        'tours': tours,
        'locations': locations,
        'current_month_name': current_month_name,
        'next_month_name': next_month_name,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'location_detail.html', context)


def go_group(request):

    current_time = datetime.datetime.now()  # текущее время
    upcoming_tours = Tour.objects.filter(start_date__gte=current_time).order_by('start_date')[:4]  # берем 4 ближайших тура, не учитывая те, что прошли
    english_to_russian_months = {
        'January': 'Январь',
        'February': 'Февраль',
        'March': 'Март',
        'April': 'Апрель',
        'May': 'Май',
        'June': 'Июнь',
        'July': 'Июль',
        'August': 'Август',
        'September': 'Сентябрь',
        'October': 'Октябрь',
        'November': 'Ноябрь',
        'December': 'Декабрь',
    }

    current_time = datetime.datetime.now()  # текущее время  timezone.now
    tours = Tour.objects.filter(start_date__gte=current_time).order_by('start_date')  # берем все следующие туры которые будут
    tours_by_month = defaultdict(list)

    for tour in tours:
        english_month = tour.start_date.strftime("%B")  # получаем месяц на английском
        russian_month = english_to_russian_months.get(english_month, english_month)  # получаем русский месяц
        tours_by_month[russian_month].append(tour)

    gids = Person.objects.all()  # Гиды
    slides = Slide.objects.filter(is_displayed=True)  # Слайды

    context = {
        'title': 'Я еду с группой',
        'upcoming_tours': upcoming_tours,
        'tours_by_month': dict(tours_by_month),
        'gids': gids,
        'slides': slides,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'go_group.html', context)


def tour_detail(request, tour_detail_slug):

    tour = Tour.objects.get(slug=tour_detail_slug)  # нынешний тур
    gids = Person.objects.all()  # Гиды

    context = {
        'title': tour.name,
        'tour': tour,
        'gids': gids,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'tour_detail.html', context)


@cache_page(60 * 5)
def blog(request):

    blogs = Blog.objects.order_by('-created_at')  # получаем все блоги
    if request.GET.get('search_blog'):
        blogs = Blog.objects.filter(name__icontains=request.GET.get('search_blog'))  # Ищем по тем данным, которые ввёл пользователь

    blog_three_items = []  # Массив заполним под массивами с блогами по три
    three = []  # под массив для blog_three_items
    for bl in blogs:
        three.append(bl)  # добавляем элемент в под массив

        if len(three) == 3:  # если там три элемента добавляем в blog_three_items и обнуляем массив
            blog_three_items.append(three)
            three = []
        else:
            if blogs.last() == bl:  # если последняя итерация(если последний элемент равен текущему), то добавляем
                blog_three_items.append(three)

    context = {
        'title': "Блоги",
        'blogs': blog_three_items,
        'search_value': request.GET.get('search_blog'),
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'blog.html', context)


@cache_page(60 * 5)
def blog_detail(request, blog_detail_slug):

    blog_item = Blog.objects.get(slug=blog_detail_slug)  # Блог
    next_blog = Blog.objects.filter(id__gt=blog_item.id).order_by('id').first()  # получаем следующий блог по id
    previous_blog = Blog.objects.filter(id__lt=blog_item.id).order_by('-id').first()  # получаем прошлый блог по id

    if next_blog:  # если следующего нет, то None, а если есть то берем его адрес
        next_blog = next_blog.get_absolute_url()
    if previous_blog:  # если прошлого нет, то None, а если есть то берем его адрес
        previous_blog = previous_blog.get_absolute_url()

    context = {
        'title': blog_item.name,
        'blog': blog_item,
        'next_blog': next_blog,
        'previous_blog': previous_blog,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'blog_detail.html', context)


def rental(request):

    products = ProductRent.objects.all()  # получаем все продукты

    context = {
        'title': "Прокат снаряжения",
        'products': products,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'rental.html', context)


@login_required
def profile(request):

    cart_init(request)  # создаем корзину если ее нет

    cart_data = request.session['cart']
    tours = cart_data['tours']  # получаем туры
    tours_items = []  # сюда закинем туры

    if len(tours) == 0:
        tours = False

    if tours:
        for tour_key, tour_val in tours.items():
            current_tour = Tour.objects.get(id=int(tour_val['id']))  # находим по id тур
            tours_items.append(current_tour)  # добавляем в массив с турами

    if request.method == 'POST':
        edit_form = UserEditForm(request.POST, instance=request.user)
        if edit_form.is_valid():
            edit_form.save()
            return redirect('travel_site:profile')
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'username': request.user.username,
            'email': request.user.email,
            'date_birth': str(request.user.date_birth) or '2000-01-01',
            'cart': cart_data,
        }
        edit_form = UserEditForm(initial=initial_data)

    context = {
        'title': "Мой профиль",
        'tours': tours_items,
        'edit_form': edit_form,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')

    return render(request, 'profile.html', context)


def cart(request):

    cart_init(request)  # создаем корзину если ее нет
    cart_info = request.session['cart']
    full = cart_info['full']  # получаем наборы
    light = cart_info['light']  # получаем наборы
    tours = cart_info['tours']  # получаем туры
    tours_items = []  # сюда закинем туры
    products = cart_info['products']  # получаем продукты
    products_items = []  # сюда закинем продукты
    if full['count'] == 0:
        full = False
    if light['count'] == 0:
        light = False
    if len(tours) == 0:
        tours = False
    if len(products) == 0:
        products = False
    if tours:
        for tour_key, tour_val in tours.items():
            current_tour = Tour.objects.get(id=int(tour_val['id']))  # находим по id тур
            tours_items.append(current_tour)  # добавляем в массив с турами

    if products:
        for product_key, product_val in products.items():
            current_tour = ProductRent  .objects.get(id=int(product_val['id']))  # находим по id продукт
            products_items.append(current_tour)  # добавляем в массив с продуктами

    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            order_instance = payment_form.save(commit=False)
            phone_first_char = request.POST['phone'][:1]
            phone = request.POST['phone']
            if phone_first_char == '7':  # если в том, что он первый символ это 7 а не например +, то добавим плюс чтобы в базе нашелся такой пользователь ибо в базе он с плюсом номер
                phone = '+' + phone
            order_instance.cart = cart_info
            order_instance.price = cart_info['price_cart']
            if request.user.is_authenticated:
                order_instance.user = request.user
            products_string = ''
            if cart_info['full']['count'] > 0:
                products_string += f"Набор фулл — {cart_info['full']['count']}\n"
            if cart_info['light']['count'] > 0:
                products_string += f"Набор лайт — {cart_info['light']['count']}\n"
            if len(cart_info['tours']) > 0:
                products_string += 'Туры\n'
                for tour in cart_info['tours'].values():
                    tour_current = Tour.objects.get(id=tour['id']).name
                    count_tour = tour['count']
                    products_string += f'{tour_current} — {count_tour}\n'
            if len(cart_info['products']) > 0:
                products_string += 'Продукты\n'
                for product in cart_info['products'].values():
                    product_current = ProductRent.objects.get(id=product['id']).name
                    count_product = product['count']
                    products_string += f'{product_current} — {count_product}\n'
            order_instance.products = products_string
            order_instance.save()
            return redirect('travel_site:cart')
    else:
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.first_name,
                'phone': request.user.username,
                'email': request.user.email,
                'date_birth': str(request.user.date_birth) or '2000-01-01',
                'cart': cart_info,
            }
            payment_form = PaymentForm(initial=initial_data)
        else:
            payment_form = PaymentForm()

    context = {
        'title': "Корзина",
        'full': full,
        'light': light,
        'tours': tours_items,
        'products': products_items,
        'payment_form': payment_form,
    }

    if forms(request, context) == 'Login':
        return redirect('travel_site:profile')
    return render(request, 'cart.html', context)


@cache_page(60 * 5)
def page_not_found(request, exception):
    return render(request, '404.html', status=404)


def cart_fetch(request):

    obj = {
        'status': 'ok',
    }

    cart_init(request)  # создаем корзину если ее нет
    full_active = False
    light_active = False
    tours_active = False
    products_active = False

    cart_data = request.session['cart']

    if 'plus_minus' in json.loads(request.body.decode()):  # Проверяем какая операция (Добавление или удаление товара)
        available = False
        cart_info = json.loads(request.body.decode())  # Информация о том, что сделал пользователь. Добавил ли он продукт, удалил набор и тд
        if 'add' in cart_info or 'remove' in cart_info:
            tours_count_max = True
            if 'add' in cart_info:
                if 'full' in cart_info:
                    cart_data['full']['count'] += 1
                    if cart_data['full']['count'] == 1:
                        cart_data['create_time'] = datetime.datetime.now().isoformat()
                    full_active = True
                    if cart_data['full']['count'] > 10:
                        cart_data['full']['count'] = 10

                elif 'light' in cart_info:
                    cart_data['light']['count'] += 1
                    if cart_data['light']['count'] == 1:
                        cart_data['create_time'] = datetime.datetime.now().isoformat()
                    light_active = True
                    if cart_data['light']['count'] > 10:
                        cart_data['light']['count'] = 10

                elif 'tour_id' in cart_info:
                    tours_active = True
                    tour_string = f"tour{cart_info['tour_id']}"
                    if tour_string not in cart_data['tours']:
                        cart_data['tours'][tour_string] = {'id': cart_info['tour_id'], 'count': 1}  # добавляем, если нет, информацию о продукте,
                    else:
                        cart_data['tours'][tour_string]['count'] += 1  # прибавляем 1 к количеству продукта
                    available = update_available_seats(cart_info['tour_id'], 'plus', cart_data['tours'][tour_string]['count'])
                    if cart_data['tours'][tour_string]['count'] > 5:
                        cart_data['tours'][tour_string]['count'] = 5
                        tours_count_max = False
                    if cart_data['tours'][tour_string]['count'] == 1:
                        cart_data['create_time'] = datetime.datetime.now().isoformat()

                elif 'product_id' in cart_info:
                    products_active = True
                    product_string = f"product{cart_info['product_id']}"
                    if product_string not in cart_data['products']:
                        cart_data['products'][product_string] = {'id': cart_info['product_id'], 'count': 1}  # добавляем, если нет, информацию о продукте,
                    else:
                        cart_data['products'][product_string]['count'] += 1  # прибавляем 1 к количеству продукта
                        if cart_data['products'][product_string]['count'] > 10:
                            cart_data['products'][product_string]['count'] = 10
                        if cart_data['products'][product_string]['count'] == 1:
                            cart_data['create_time'] = datetime.datetime.now().isoformat()

            elif 'remove' in cart_info:
                if 'full' in cart_info:
                    cart_data['full']['count'] -= 1
                    if cart_data['full']['count'] < 0:
                        cart_data['full']['count'] = 0
                    full_active = True

                elif 'light' in cart_info:
                    cart_data['light']['count'] -= 1
                    if cart_data['light']['count'] < 0:
                        cart_data['light']['count'] = 0
                    light_active = True

                elif 'tour_id' in cart_info:
                    tours_active = True
                    tour_string = f"tour{cart_info['tour_id']}"
                    if tour_string not in cart_data['tours']:
                        cart_data['tours'][tour_string] = {'id': cart_info['tour_id'], 'count': 0}  # добавляем, если нет, информацию о продукте,
                    else:
                        cart_data['tours'][tour_string]['count'] -= 1  # отнимаем 1 к количеству продукта
                    available = update_available_seats(cart_info['tour_id'], 'minus', cart_data['tours'][tour_string]['count'])
                    if cart_data['tours'][tour_string]['count'] < 1:
                        del cart_data['tours'][tour_string]

                else:
                    products_active = True
                    product_string = f"product{cart_info['product_id']}"
                    if product_string not in cart_data['products']:
                        cart_data['products'][product_string] = {'id': cart_info['product_id'], 'count': 0}  # добавляем, если нет, информацию о продукте,
                    else:
                        cart_data['products'][product_string]['count'] -= 1  # отнимаем 1 к количеству продукта
                    if cart_data['products'][product_string]['count'] < 1:
                        del cart_data['products'][product_string]
            total = ''
            if full_active:  # находим тот элемент, на который нажали и передаем его в js
                total = cart_data['full']
            elif light_active:  # находим тот элемент, на который нажали и передаем его в js
                total = cart_data['light']
            elif tours_active:  # находим тот элемент, на который нажали и передаем его в js
                tour_string = f"tour{cart_info['tour_id']}"
                if tour_string in cart_data['tours']:  # находим тот элемент, на который нажали и передаем его в js
                    total = cart_data['tours'][tour_string]
                else:
                    total = {}
            elif products_active:  # находим тот элемент, на который нажали и передаем его в js
                product_string = f"product{cart_info['product_id']}"
                if product_string in cart_data['products']:
                    total = cart_data['products'][product_string]
                else:
                    total = {}
            request.session.modified = True
            obj = {
                'status': 'ok',
                'item': total,
                'available': available,
                'tours_count_max': tours_count_max,
            }

    elif 'count_products' in json.loads(request.body.decode()):   # Проверяем какая операция (подсчет товаров)
        count_full = cart_data['full']['count']
        count_light = cart_data['light']['count']
        count_tours_array = []
        count_products_array = []

        for item, value in cart_data['tours'].items():
            count_tours_array.append(value)  # закидываем в массив туры

        for item, value in cart_data['products'].items():
            count_products_array.append(value)  # закидываем в массив продукты
        quantity_products = {
            'full': count_full,
            'light': count_light,
            'products': count_products_array,
            'tours': count_tours_array
        }

        obj = {
            'status': 'ok',
            'quantity_products': quantity_products,
        }

    elif 'delete_product' in json.loads(request.body.decode()):  # Проверяем какая операция (удаление товара)
        available = False
        delete_product_id = json.loads(request.body.decode())['id']  # id товара, который будет удалён
        type_product = json.loads(request.body.decode())['name']  # тип товара (что мы удаляем: продукт, набор или тур)
        if type_product == 'full' or type_product == 'light':
            cart_data[type_product] = {'count': 0}
        elif type_product == 'tours':
            tour_string = 'tour' + delete_product_id
            available = update_available_seats(delete_product_id, 'delete_product', cart_data['tours'][tour_string]['count'])
            del cart_data['tours'][tour_string]
        elif type_product == 'products':
            product_string = 'product' + delete_product_id
            del cart_data['products'][product_string]
        obj = {
            'status': 'ok',
            'cart': cart_data,
            'available': available,
        }
        request.session.modified = True

    elif 'summa' in json.loads(request.body.decode()):  # Проверяем какая операция (стоимость корзины)
        cart_data['price_cart'] = json.loads(request.body.decode())['summa']
        request.session.modified = True
    return JsonResponse(obj)
