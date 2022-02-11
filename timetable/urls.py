from django.urls import path

from . import views

from timetable.views import *

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('test/', views.test, name='test'),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('dashboard2/', views.dashboard2, name='dashboard2'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboardadmin/', views.dashboardadmin, name='dashboardadmin'),


    path('addclass/', views.addclass, name='addclass'),

    path('addsubject/', views.addsubject, name='addsubject'),
    
    path('addteacher/', views.addteacher, name='addteacher'),

    path('addclassroom/', views.addclassroom, name='addclassroom'),

    path('timetable/<int:semester>/<section>/',
         views.timetable, name='timetable'),
     path('timetablestudent/<int:semester>/<section>/',
         views.timetablestudent, name='timetablestudent'),
    path('faculty/<teacher>/',
         views.facultytimetable, name='facultytimetable'),

    path('cwtt/<teacher>/',
         views.cwtt_timetable, name='cwtt_print'), 

     path('facultyadmin/<teacher>/',
         views.facultytimetableadmin, name='facultytimetableadmin'),

    path('faculty/',views.faculty, name='faculty'),
    
    path('cwtt/',views.cwtt, name='cwtt'),

    path('facultyadmin/',views.facultyadmin, name='facultyadmin'),

    path('pdf_download/<int:semester>/<section>/', views.DownloadPDF, name="pdf_download"),
    path('pdf_download/<teacher>/', views.facultypdfdownload, name="faculty_pdf_download"),
    path('pdf_download/<teacher>/', views.cwttpdfdownload, name="cwtt_pdf_download"),
    #changes in here-----------------
    
    #-----------------------------------------
   
    path('v_subs/', views.subs_crud, name='v_subs'),
    path('delete/<int:id>/', views.delete_data, name='deletedata'),
    path('<int:id>/', views.update_data, name='updatedata'),

]
