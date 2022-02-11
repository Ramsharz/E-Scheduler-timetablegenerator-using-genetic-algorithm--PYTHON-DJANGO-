from django import forms
from django.contrib.auth import get_user_model

from django.contrib.auth.forms import UserCreationForm

from .models import Resource, Staff, Schedule, Class, Course

from django.contrib.auth.models import User
from django.core import validators

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class SubjectForm(forms.ModelForm):
    section_choices = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E')
    )
    section = forms.MultipleChoiceField(choices=section_choices, initial="A", widget=forms.CheckboxSelectMultiple())

    name = forms.CharField(validators=[validators.MaxLengthValidator(20)])


    class Meta:
        model = Course
        fields = ['code', 'name', 'type', 'credit_hours', 'classes_per_week', 'semester_number']


class TeacherForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = Staff
        fields = '__all__'


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = '__all__'


class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = '__all__'

    
    #allowed_classrooms = forms.ModelMultipleChoiceField(
        #queryset=Resource.objects.all(),
        #widget=forms.CheckboxSelectMultiple
    #)

    def save(self, commit=True):
        # Get the unsaved Pizza instance
        instance = forms.ModelForm.save(self, False)

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            # This is where we actually link the pizza with toppings
            instance.allowed_classrooms.clear()
            for course in self.cleaned_data['allowed_classrooms']:
                instance.allowed_classrooms.add(course)

        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        # Just like this
        # if commit:
        instance.save()
        old_save_m2m()
        # self.save_m2m()

        return instance

