from django import forms
from .models import Activity
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Category, Subcategory
from django.forms.widgets import Select


class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с такой почтой уже существует.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует.")
        return phone
    

class CustomSelect(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:  # Если значение существует
            category = Subcategory.objects.get(pk=value)
            option['attrs']['style'] = f'background-color: {category.category.color};'
        return option


class ActivityForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),  # Используем все категории из базы данных
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Категория"
    )

    class Meta:
        model = Activity
        fields = [
            'name', 
            'category',
            'subcategory', 
            'goal', 
            'description', 
            'value', 
            'start_time', 
            'end_time'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название действия'}),
            'subcategory': CustomSelect(attrs={'class': 'form-select'}),
            'goal': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Значение'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'name': 'Название действия',
            'category': 'Категория',
            'subcategory': 'Подкатегория',
            'goal': 'Цель',
            'description': 'Описание',
            'value': 'Значение',
            'start_time': 'Время начала',
            'end_time': 'Время окончания',
        }