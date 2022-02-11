import os

import pdfkit
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse

# from weasyprint import HTML
from django.template import Context, context
from django.template.loader import render_to_string, get_template

# Create your models here.

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Class, Resource, Course, Staff, Schedule
from .forms import SubjectForm, ClassForm, TeacherForm, ClassRoomForm, UserRegisterForm

from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings

from django.forms.models import model_to_dict
import random
from .scheduler import main
import json
import csv
import datetime

import tempfile

from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

from django.http import *
from .models import *

User = get_user_model()


@login_required
def test(request):
    if request.method == "POST":
        form = ClassForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():

            print('----valid')
            data = form.save()
            print('----saved')

            # data.save()
            # form.save_m2m()
        else:
            print(form.errors)

    form = {'form': ClassRoomForm(), 'form1': ClassForm()}
    return render(request, 'test.html', form)

@login_required()
def addclass(request):
    if request.method == "POST":
        form = ClassForm(request.POST, request.FILES)
        if form.is_valid():
            print('----valid')
            data = form.save()
            Schedule.objects.all().delete()
            d = createjsoninput()
            print(d)
            main()

            print('----saved')
            print('--------time table created------------')
            messages.success(
                request, 'Class added successfully', extra_tags="alert")
            messages.success(
                request, 'Timetable Created successfully', extra_tags="alert")
        else:
            print(form.errors)

         

    form = {'form': ClassForm(), 'form1': ClassForm()}
    return render(request, 'class.html', form)


@login_required
def addsubject(request):
    if request.method == "POST":

        form = SubjectForm(request.POST, request.FILES)
        if form.is_valid():
            vals = form.cleaned_data['section']

            #form.cleaned_data['section'] = v[0]
            print('----valid')

            for i in vals:
                form = SubjectForm(request.POST, request.FILES)
                if form.is_valid():
                    form.instance.section = i
                    obj = form.save()
                    print('----saved')
            messages.success(
                request, 'Subject added successfully', extra_tags="alert")
        else:
            messages.error(
                request, 'Enter Correct Format', extra_tags="alert")
            print(form.errors)

    form = {'form': SubjectForm(), 'form1': ClassForm()}
    return render(request, 'subject.html', form)


@login_required
def addclassroom(request):
    if request.method == "POST":
        form = ClassRoomForm(request.POST, request.FILES)
        if form.is_valid():
            print('----valid')
            data = form.save()
            print('----saved')
            messages.success(
                request, 'Classroom added successfully', extra_tags="alert")
        else:
            messages.error(
                request, 'Enter Correct Format', extra_tags="alert")
            print(form.errors)

    form = {'form': ClassRoomForm(), 'form1': ClassForm()}
    return render(request, 'classroom.html', form)

@login_required
def dashboardadmin(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.save()
        else:
            print(form.errors)

    form = {'form': TeacherForm(), 'form1': ClassForm()}
    
    return render(request, 'dashboardadmin.html', form)

@login_required
def addteacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            print('----valid')
            data = form.save()
            print('----saved')
            messages.success(
                request, 'Teacher added successfully', extra_tags="alert")
        else:
            messages.error(
                request, 'Incorrect Format, please enter valid data in the fields.', extra_tags="alert")
            print(form.errors)

    form = {'form': TeacherForm(), 'form1': ClassForm()}
    return render(request, 'teacher.html', form)


def dashboard(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.save()
        else:
            print(form.errors)

    form = {'form': TeacherForm(), 'form1': ClassForm()}
    
    return render(request, 'dashboard.html', form)

    

# Changes in here @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@login_required
def dashboard2(request):
   
    Courses = Course.objects.all().count()
    Staffmembers = Staff.objects.all().count()
    Totalrooms = Resource.objects.all().count()
    Totalschedules = Schedule.objects.all().count()
    
    context = {
        'Courses' : Courses,
        'Staffmembers' : Staffmembers,
        'Totalrooms' : Totalrooms,
        'Totalschedules' : Totalschedules,

    }

    return render(request, 'dashboard2.html', context)
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    

@login_required
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            print('----valid')
            data = form.save()
            print('----saved')
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Your account has been created! You can now login!')
            print(11, username, User.objects.all())
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})


def createjsoninput():
    objs = Class.objects.all()
    classrooms_labs = Resource.objects.filter(type='lab')
    classrooms_lectures = Resource.objects.filter(type='lecture')
    labs = [i.name for i in classrooms_labs]
    lectures = [i.name for i in classrooms_lectures]

    d = {
        'Classrooms': {
            'lab': labs,
            'lecture': lectures
        },
        'Classes': []
    }
    classes = []
    for i in objs:
        teacher = i.teacher.name
        subject = i.subject.name
        semester = i.subject.semester_number
        section = i.subject.section
        duration = i.subject.credit_hours
        per_week = i.subject.classes_per_week
        type = i.subject.type
        if per_week > duration:
            per_week = duration
        if duration == 3 and type == 'lecture':
            if per_week == 1:
                classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                    str(semester) + section], 'Type': type, 'Duration': '3', 'Classroom': type})
            else:
                if per_week == 2:
                    classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                        str(semester) + section], 'Type': type, 'Duration': '1', 'Classroom': type})
                    classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                        str(semester) + section], 'Type': type, 'Duration': '2', 'Classroom': type})
                else:
                    classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                        str(semester) + section], 'Type': type, 'Duration': '1', 'Classroom': type})
                    classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                        str(semester) + section], 'Type': type, 'Duration': '1', 'Classroom': type})
                    classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                        str(semester) + section], 'Type': type, 'Duration': '1', 'Classroom': type})

        elif duration == 2 and type == 'lecture':
            if per_week == 1:
                classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                    str(semester) + section], 'Type': type, 'Duration': '2', 'Classroom': type})
            else:
                classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                    str(semester) + section], 'Type': type, 'Duration': '1', 'Classroom': type})
                classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                    str(semester) + section], 'Type': type, 'Duration': '1', 'Classroom': type})
        elif duration == 1 and type == 'lecture':
            classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                str(semester) + section], 'Type': type, 'Duration': '1', 'Classroom': type})
        elif type == 'lab':
            classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                str(semester) + section], 'Type': type, 'Duration': '2', 'Classroom': type})
        '''
        elif duration == 1 and type == 'lab':
            classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                           str(semester)+section], 'Type': type, 'Duration': '2', 'Classroom': type})
        elif duration == 2 and type == 'lab':
            classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                           str(semester)+section], 'Type': type, 'Duration': '2', 'Classroom': type})
            classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                           str(semester)+section], 'Type': type, 'Duration': '2', 'Classroom': type})
        elif duration == 3 and type == 'lab':
            classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                           str(semester)+section], 'Type': type, 'Duration': '2' 'Classroom': type})
            classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                           str(semester)+section], 'Type': type, 'Duration': '2', 'Classroom': type})
            classes.append({'Subject': subject, 'Teacher': teacher, 'Group': [
                           str(semester)+section], 'Type': type, 'Duration': '2', 'Classroom': type})
                           '''

    d['Classes'] = classes
    with open('test_files/data.txt', 'w') as outfile:
        json.dump(d, outfile, indent=4)
    return json.dumps(d)


def timetable_data(semester, section):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = ['9', '10', '11', '12', '1 ', '2 ']
    schedule = Schedule.objects.filter(semester=semester, section=section)

    table1 = []
    for hour in hours:
        row = []
        for day in days:
            row.append(schedule.filter(time_slot__startswith=hour,
                                       day=day).first())
        table1.append(row)
    print(row)
    table2 = []
    for hour in hours:
        row = []
        for day in days:
            if hour == '1 ':
                query = Q(time_slot__endswith='1') & ~Q(
                    time_slot__endswith='11')
                row.append(schedule.filter(query,
                                           day=day).first())
            elif hour == '2 ':
                query = Q(time_slot__endswith='2') & ~Q(
                    time_slot__endswith='12')
                row.append(schedule.filter(query,
                                           day=day).first())
            else:
                row.append(schedule.filter(time_slot__endswith=hour.replace(' ', ''),
                                           day=day).first())
        table2.append(row)
    table = []
    for i in range(len(table1)):
        row = []
        for j in range(len(table1[0])):

            if table1[i][j] is not None:
                subject = table1[i][j].subject
                teacher = table1[i][j].teacher
                type = table1[i][j].type
                room = table1[i][j].room
                row.append([subject, teacher, type, room])
            elif table2[i][j] is not None:

                subject = table2[i][j].subject
                teacher = table2[i][j].teacher
                type = table2[i][j].type
                room = table2[i][j].room
                row.append([subject, teacher, type, room])
            else:
                row.append('')
        table.append(row)

    context = {
        'semester': semester,
        'section': section,
        'table': table
    }
    return context


def timetable(request, semester, section):
    context = timetable_data(semester, section)
    print(context)
    return render(request, 'time_table.html', context)

def timetable_datastudent(semester, section):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    hours = ['9', '10', '11', '12', '1 ', '2 ']
    schedule = Schedule.objects.filter(semester=semester, section=section)

    table1 = []
    for hour in hours:
        row = []
        for day in days:
            row.append(schedule.filter(time_slot__startswith=hour,
                                       day=day).first())
        table1.append(row)
    print(row)
    table2 = []
    for hour in hours:
        row = []
        for day in days:
            if hour == '1 ':
                query = Q(time_slot__endswith='1') & ~Q(
                    time_slot__endswith='11')
                row.append(schedule.filter(query,
                                           day=day).first())
            elif hour == '2 ':
                query = Q(time_slot__endswith='2') & ~Q(
                    time_slot__endswith='12')
                row.append(schedule.filter(query,
                                           day=day).first())
            else:
                row.append(schedule.filter(time_slot__endswith=hour.replace(' ', ''),
                                           day=day).first())
        table2.append(row)
    table = []
    for i in range(len(table1)):
        row = []
        for j in range(len(table1[0])):

            if table1[i][j] is not None:
                subject = table1[i][j].subject
                teacher = table1[i][j].teacher
                type = table1[i][j].type
                room = table1[i][j].room
                row.append([subject, teacher, type, room])
            elif table2[i][j] is not None:

                subject = table2[i][j].subject
                teacher = table2[i][j].teacher
                type = table2[i][j].type
                room = table2[i][j].room
                row.append([subject, teacher, type, room])
            else:
                row.append('')
        table.append(row)

    context = {
        'semester': semester,
        'section': section,
        'table': table
    }
    return context


def timetablestudent(request, semester, section):
    context = timetable_datastudent(semester, section)
    print(context)
    return render(request, 'time_tablestudent.html', context)

# changes in here--------------------------------------------------------------
def cwtt(request):
    teachers = Course.objects.all()
    context = {
        'teachers': teachers
    }
    return render(request, 'cwtt.html', context)

def cwtt_data(teacher):
    teachers = Course.objects.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = ['9', '10', '11', '12', '1 ', '2 ']
    schedule = Schedule.objects.filter(subject=teacher)

    table1 = []
    h = None
    ss = {}
    for day in days:
        ss[day] = None
    for hour in hours:
        row = []
        for day in days:
            s = schedule.filter(time_slot__startswith=hour,
                                day=day).first()

            if ss[day] is not None:
                row.append(ss[day])
                ss[day] = None
            else:
                row.append(s)
            if s is not None:
                if int(s.duration) == 3:
                    ss[day] = schedule.filter(time_slot__startswith=hour,
                                              day=day).first()
                else:
                    ss[day] = None
            else:
                ss[day] = None

        table1.append(row)
    print(table1)
    print()
    table2 = []
    for hour in hours:
        row = []
        for day in days:
            if hour == '1 ':
                query = Q(time_slot__endswith='1') & ~Q(
                    time_slot__endswith='11')
                row.append(schedule.filter(query,
                                           day=day).first())
            elif hour == '2 ':
                query = Q(time_slot__endswith='2') & ~Q(
                    time_slot__endswith='12')
                row.append(schedule.filter(query,
                                           day=day).first())
            else:
                row.append(schedule.filter(time_slot__endswith=hour.replace(' ', ''),
                                           day=day).first())
        table2.append(row)
    table = []
    for i in range(len(table1)):
        row = []
        for j in range(len(table1[0])):

            if table1[i][j] is not None:
                subject = table1[i][j].subject
                semester = table1[i][j].semester
                section = table1[i][j].section
                type = table1[i][j].type
                room = table1[i][j].room
                row.append([subject, str(semester) + section, type, room])
            elif table2[i][j] is not None:

                subject = table2[i][j].subject
                semester = table2[i][j].semester
                section = table2[i][j].section
                type = table2[i][j].type
                room = table2[i][j].room
                row.append([subject, str(semester) + section, type, room])
            else:
                row.append('')
        table.append(row)

    context = {
        'teachers': teachers,
        'teacher': teacher,
        'table': table
    }
    return context


def cwtt_timetable(request, teacher):
    context = cwtt_data(teacher)
    return render(request, 'cwtt_print.html', context)



# ------------------------------------------------------------------------------

def faculty(request):
    teachers = Staff.objects.all()
    context = {
        'teachers': teachers
    }
    return render(request, 'facultydashboard.html', context)

def facultyadmin(request):
    teachers = Staff.objects.all()
    context = {
        'teachers': teachers
    }
    return render(request, 'facultydashboardadmin.html', context)



def facultytimetable_data(teacher):
    teachers = Staff.objects.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = ['9', '10', '11', '12', '1 ', '2 ']
    schedule = Schedule.objects.filter(teacher=teacher)

    table1 = []
    h = None
    ss = {}
    for day in days:
        ss[day] = None
    for hour in hours:
        row = []
        for day in days:
            s = schedule.filter(time_slot__startswith=hour,
                                day=day).first()

            if ss[day] is not None:
                row.append(ss[day])
                ss[day] = None
            else:
                row.append(s)
            if s is not None:
                if int(s.duration) == 3:
                    ss[day] = schedule.filter(time_slot__startswith=hour,
                                              day=day).first()
                else:
                    ss[day] = None
            else:
                ss[day] = None

        table1.append(row)
    print(table1)
    print()
    table2 = []
    for hour in hours:
        row = []
        for day in days:
            if hour == '1 ':
                query = Q(time_slot__endswith='1') & ~Q(
                    time_slot__endswith='11')
                row.append(schedule.filter(query,
                                           day=day).first())
            elif hour == '2 ':
                query = Q(time_slot__endswith='2') & ~Q(
                    time_slot__endswith='12')
                row.append(schedule.filter(query,
                                           day=day).first())
            else:
                row.append(schedule.filter(time_slot__endswith=hour.replace(' ', ''),
                                           day=day).first())
        table2.append(row)
    table = []
    for i in range(len(table1)):
        row = []
        for j in range(len(table1[0])):

            if table1[i][j] is not None:
                subject = table1[i][j].subject
                semester = table1[i][j].semester
                section = table1[i][j].section
                type = table1[i][j].type
                room = table1[i][j].room
                row.append([subject, str(semester) + section, type, room])
            elif table2[i][j] is not None:

                subject = table2[i][j].subject
                semester = table2[i][j].semester
                section = table2[i][j].section
                type = table2[i][j].type
                room = table2[i][j].room
                row.append([subject, str(semester) + section, type, room])
            else:
                row.append('')
        table.append(row)

    context = {
        'teachers': teachers,
        'teacher': teacher,
        'table': table
    }
    return context


def facultytimetable(request, teacher):
    context = facultytimetable_data(teacher)
    return render(request, 'faculty.html', context)


def facultytimetable_dataadmin(teacher):
    teachers = Staff.objects.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = ['9', '10', '11', '12', '1 ', '2 ']
    schedule = Schedule.objects.filter(teacher=teacher)

    table1 = []
    h = None
    ss = {}
    for day in days:
        ss[day] = None
    for hour in hours:
        row = []
        for day in days:
            s = schedule.filter(time_slot__startswith=hour,
                                day=day).first()

            if ss[day] is not None:
                row.append(ss[day])
                ss[day] = None
            else:
                row.append(s)
            if s is not None:
                if int(s.duration) == 3:
                    ss[day] = schedule.filter(time_slot__startswith=hour,
                                              day=day).first()
                else:
                    ss[day] = None
            else:
                ss[day] = None

        table1.append(row)
    print(table1)
    print()
    table2 = []
    for hour in hours:
        row = []
        for day in days:
            if hour == '1 ':
                query = Q(time_slot__endswith='1') & ~Q(
                    time_slot__endswith='11')
                row.append(schedule.filter(query,
                                           day=day).first())
            elif hour == '2 ':
                query = Q(time_slot__endswith='2') & ~Q(
                    time_slot__endswith='12')
                row.append(schedule.filter(query,
                                           day=day).first())
            else:
                row.append(schedule.filter(time_slot__endswith=hour.replace(' ', ''),
                                           day=day).first())
        table2.append(row)
    table = []
    for i in range(len(table1)):
        row = []
        for j in range(len(table1[0])):

            if table1[i][j] is not None:
                subject = table1[i][j].subject
                semester = table1[i][j].semester
                section = table1[i][j].section
                type = table1[i][j].type
                room = table1[i][j].room
                row.append([subject, str(semester) + section, type, room])
            elif table2[i][j] is not None:

                subject = table2[i][j].subject
                semester = table2[i][j].semester
                section = table2[i][j].section
                type = table2[i][j].type
                room = table2[i][j].room
                row.append([subject, str(semester) + section, type, room])
            else:
                row.append('')
        table.append(row)

    context = {
        'teachers': teachers,
        'teacher': teacher,
        'table': table
    }
    return context

def facultytimetableadmin(request, teacher):
    context = facultytimetable_dataadmin(teacher)
    return render(request, 'facultyadmin.html', context)


def facultypdfdownload(request, teacher):
    context = facultytimetable_data(teacher)
    pdf = render_to_pdf('faculty_timetable_pdf.html', context, True)
    response = HttpResponse(pdf)
    response['Content-Type'] = 'application/pdf'
    response['Content-disposition'] = 'attachment ; filename = faculty_timetable.pdf'
    return response

data = {
    "company": "Dennnis Ivanov Company",
    "address": "123 Street name",
    "city": "Vancouver",
    "state": "WA",
    "zipcode": "98663",

    "phone": "555-555-2345",
    "email": "youremail@dennisivy.com",
    "website": "dennisivy.com",

}

def cwttpdfdownload(request, teacher):
    context = cwtt_data(teacher)
    pdf = render_to_pdf('faculty_timetable_pdf.html', context, True)
    response = HttpResponse(pdf)
    response['Content-Type'] = 'application/pdf'
    response['Content-disposition'] = 'attachment ; filename = faculty_timetable.pdf'
    return response

data = {
    "company": "Dennnis Ivanov Company",
    "address": "123 Street name",
    "city": "Vancouver",
    "state": "WA",
    "zipcode": "98663",

    "phone": "555-555-2345",
    "email": "youremail@dennisivy.com",
    "website": "dennisivy.com",

}



def render_to_pdf(template_src, context_dict, faculty=False):
    # Create and return response with created pdf
    template = get_template(template_src)
    html = template.render(context_dict)
    if not faculty:
        file = open("sample.html", "w")
        file.write(html)
        file.close()
        options = {
            "enable-local-file-access": None
        }   
        pdf = pdfkit.from_file('sample.html', False, options=options)
        os.remove("sample.html")
    else:
        file = open("sample_faculty.html", "w")
        file.write(html)
        file.close()
        options = {
            "enable-local-file-access": None
        }   
        pdf = pdfkit.from_file('sample_faculty.html', False,options=options)
        os.remove("sample_faculty.html")

    return pdf

# Automaticly downloads to PDF file


def DownloadPDF(request, semester, section):
    context = timetable_data(semester, section)
    pdf = render_to_pdf('pdf-output.html', context)
    response = HttpResponse(pdf)
    response['Content-Type'] = 'application/pdf'
    response['Content-disposition'] = 'attachment ; filename = timetable.pdf'
    return response


def index(request):
    context = {}
    return render(request, 'pdf-output.html', context)

# This function will show ALL Course Items
def subs_crud(request):
    stud = Course.objects.all()
    return render(request, 'subject.html', {'stu': stud})


# This Function will delete
def delete_data(request, id):
    if request.method == 'POST':
        pi = Course.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect('/')


# This Function Will Update/Edit
def update_data(request, id):
    if request.method == 'POST':
        pi = Course.objects.get(pk=id)
        fm = SubjectForm(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
        else:
            pi = Course.objects.get(pk=id)
            fm = SubjectForm(instance=pi)
        return render(request, 'v_subs-crud.html', {'form': fm})

#views for Counting Dashboard
def count(request):
    Courses = Course.objects.all()
    
    context = {
        'Courses' : Courses
    }

    return render(request,'subject.html',context)
