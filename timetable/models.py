from django.core import validators
from django.db import models
import ast
from django_extensions.db.fields import AutoSlugField
import json
from django.core.validators import RegexValidator

class Staff(models.Model):
    alphanumeric = RegexValidator(regex='^[A-Za-z]*$', message='Name field must be Alphabetic')
    name = models.CharField(max_length=255, validators = [alphanumeric])
    phone_regex = RegexValidator(regex = r"^\+?1?\d{8,15}$", message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile_number = models.CharField(validators = [phone_regex], max_length = 16, unique = True)
    email = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

# subject


class Course(models.Model):
    type_choices = (
        ('lab', 'Lab'),
        ('lecture', 'Lecture')
    )
    semester_choices = (
        (1, '1st'),
        (2, '2nd'),
        (3, '3rd'),
        (4, '4th'),
        (5, '5th'),
        (6, '6th'),
        (7, '7th'),
        (8, '8th')
    )
    credit_choices = (
        (1, '1 hour'),
        (2, '2 hours'),
        (3, '3 hours')
    )
    classes_choices = (
        (1, '1'),
        (2, '2'),
        (3, '3')
    )
    section_choices = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E')
    )
    code = models.CharField(max_length=20)
    alpha = RegexValidator(regex='^[A-Za-z]*$', message='Name field must be Alphabetic')
    name = models.CharField(max_length=255, validators = [alpha])
    type = models.CharField(max_length=50, choices=type_choices)
    credit_hours = models.IntegerField(choices=credit_choices)
    classes_per_week = models.IntegerField(choices=classes_choices)
    semester_number = models.IntegerField(choices=semester_choices)
    section = models.CharField(max_length=1, choices=section_choices)

    def __str__(self):
        return 'Subject: '+self.code+'-'+self.name+' ('+self.type+')'+', Semester: '+str(self.semester_number)+', Section: '+self.section+', Credit hours: '+str(self.credit_hours)+', Classes per week: '+str(self.classes_per_week)

# classroom


class Resource(models.Model):
    type_choices = (
        ('lab', 'Lab'),
        ('lecture', 'Lecture')
    )
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=50, choices=type_choices)
    numeric = RegexValidator(regex='^[1-9]', message='capacity field must be numeric value')
    capacity = models.IntegerField(blank=True, null=True, validators = [numeric])

    def __str__(self):
        return self.name+' ('+self.type+')'


class Schedule(models.Model):
    teacher = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    room = models.CharField(max_length=100)
    time_slot = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    day = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    semester = models.IntegerField()
    section = models.CharField(max_length=1)
   

    def __str__(self):
        return 'Subject: '+self.subject+' ('+self.type+')'+', Teacher: '+self.teacher+', Semester: '+str(self.semester)+', Section: '+self.section+', Room: '+self.room+', Day: '+self.day+', Time: '+str(self.time_slot)+', Duration: '+self.duration


class Class(models.Model):
    teacher = models.ForeignKey(
        'Staff', on_delete=models.CASCADE)
    subject = models.ForeignKey(
        'Course', on_delete=models.CASCADE)

    def __str__(self):
        return 'Subject: '+self.subject.code+'-'+self.subject.name+' ('+self.subject.type+')'+', Teacher: '+self.teacher.name+', Semester: '+str(self.subject.semester_number)+', Section: '+self.subject.section+', Credit hours: '+str(self.subject.credit_hours)
