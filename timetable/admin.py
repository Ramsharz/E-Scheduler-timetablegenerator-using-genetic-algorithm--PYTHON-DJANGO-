from django.contrib import admin
from .models import Staff, Schedule, Resource, Class, Course
# Register your models here.
admin.site.register(Staff)
admin.site.register(Schedule)
admin.site.register(Resource)
admin.site.register(Class)
admin.site.register(Course)
