from django import forms
from .models import Activity, Goal
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
    new_subcategory_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Создать новую подкатегорию'}),
        label="Создать новую подкатегорию"
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
    
    def clean(self):
        cleaned_data = super().clean()
        new_subcategory_name = cleaned_data.get('new_subcategory_name')
        category = cleaned_data.get('category')

        if new_subcategory_name:
            if not category:
                raise forms.ValidationError("Выберите категорию для новой подкатегории.")
            if Subcategory.objects.filter(name=new_subcategory_name, category=category).exists():
                raise forms.ValidationError("Подкатегория с таким именем уже существует в выбранной категории.")

        return cleaned_data


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            'name', 'category', 'subcategory', 'description', 'target_value', 'period', 'start_date', 'end_date', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Читать книгу'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Описание цели'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Целевое значение (ч)'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Название цели',
            'category': 'Категория',
            'subcategory': 'Подкатегория',
            'description': 'Описание',
            'target_value': 'Целевое значение (ч)',
            'period': 'Период',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'status': 'Статус',
        }