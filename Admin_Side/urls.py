from django.urls import path
from Admin_Side import views

urlpatterns = [
    path('indexpage/',views.indexpage,name="indexpage"),
    path('admin_login_page/',views.admin_login_page,name="admin_login_page"),
    path('admin_login/',views.admin_login,name="admin_login"),
    path('admin_reg_page/',views.admin_reg_page,name="admin_reg_page"),
    path('admin_reg_save/',views.admin_reg_save,name="admin_reg_save"),
    path('display_user/',views.display_user,name="display_user"),
    path('display_complaint/',views.display_complaint,name="display_complaint"),
    path('display_contact/',views.display_contact,name="display_contact"),
    path('warned_users_page/', views.warned_users_page, {'count': 1}, name='warned_users_page'),
    path('warned_users_page/<int:count>/',views.warned_users_page,name="warned_users_page"),

]