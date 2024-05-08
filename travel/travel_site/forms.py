from django import forms
from django.core.exceptions import ValidationError
from .models import *
from phonenumber_field.formfields import PhoneNumberField


class UserRegisterForm(forms.ModelForm):

    phone = PhoneNumberField(max_length=12,  widget=forms.NumberInput(
        attrs={'class': 'form-input phone-input-register', 'placeholder': 'Номер телефона'}),
                error_messages={'invalid': 'Введите корректный номер телефона (например, +71234567890)'})
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Имя Фамилия', 'maxlength': 60}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Пароль еще раз'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-input', 'placeholder': 'Почта', 'maxlength': 120}))

    class Meta:
        model = User
        fields = ['first_name', 'phone', 'email', 'password1', 'password2']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if any(char.isdigit() for char in first_name):
            raise ValidationError("Имя Фамилия не должны содержать цифр и следующих знаков:@+")
        return first_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Пользователь с таким номером уже существует")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой электронной почтой уже существует")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError("Пароли не совпадают")
        if len(password1) < 4:
            raise ValidationError("Длина пароля не может быть меньше 4")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')  # Получаем пароль из формы
        user.password = password
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    data = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Имя Фамилия | Номер телефона | Почта', 'maxlength': 60}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Пароль'}))


class PaymentForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Лилия Воронова', 'maxlength': 60}), label='Имя Фамилия')
    phone = PhoneNumberField(max_length=12, widget=forms.NumberInput(
        attrs={'class': 'form-input phone-input-register', 'id': 'phone-input-register-payment', 'placeholder': '+7 555 55 25 26'}),
                             error_messages={'invalid': 'Введите корректный номер телефона (например, +7 123 456 78 90)'}, label='Номер телефона')
    date_birth = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-input', 'type': 'date'}), label='Дата рождения', required=False)
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-input', 'id': 'payment_email_id', 'placeholder': 'tourfan@mail.com', 'maxlength': 120}), label='Почта')

    class Meta:
        model = Order
        fields = ['name', 'phone', 'date_birth', 'email']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if any(char.isdigit() for char in name):
            raise ValidationError("Имя Фамилия не должны содержать цифр и следующих знаков:@+")
        return name
        
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Пользователь с таким номером уже существует")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой электронной почтой уже существует")
        return email


class UserEditForm(forms.ModelForm):

    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Лилия Воронова', 'maxlength': 60}), label='Имя Фамилия')
    username = PhoneNumberField(max_length=12, widget=forms.NumberInput(
        attrs={'class': 'form-input', 'id': 'phone-input-register-edit', 'placeholder': '+7 555 55 25 26'}),
                             error_messages={'invalid': 'Введите корректный номер телефона (например, +7 123 456 78 90)'}, label='Номер телефона')
    date_birth = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-input', 'type': 'date'}), label='Дата рождения', required=False)
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-input', 'id': 'user_edit_id', 'placeholder': 'tourfan@mail.com', 'maxlength': 120}), label='Почта')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'date_birth', 'email']

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name')
        if any(char.isdigit() for char in name):
            raise ValidationError("Имя Фамилия не должны содержать цифр и следующих знаков:@+")
        return name


class PasswordForgetUserForm(forms.Form):
    forget = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-input', 'placeholder': 'Почта', 'maxlength': 60}))


class PasswordResetUserForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Пароль еще раз'}))

    class Meta:
        model = User
        fields = ['password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError("Пароли не совпадают")
        if len(password1) < 4:
            raise ValidationError("Длина пароля не может быть меньше 4")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')  # Получаем пароль из формы
        user.password = password
        if commit:
            user.save()
        return user
