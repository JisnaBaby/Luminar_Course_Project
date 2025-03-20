from django.urls import path
from Web_Side import views
urlpatterns = [
    path('user_login_page/', views.user_login_page, name="user_login_page"),
    path('', views.homepage, name="homepage"),
    path('reg_page/', views.reg_page, name="reg_page"),
    path('profile_page/', views.profile_page, name="profile_page"),
    path('cyber_course/', views.cyber_course, name="cyber_course"),
    path('bullying_course/', views.bullying_course, name="bullying_course"),
    path('quiz_register/', views.register_quiz, name='quiz_register'),
    path('quiz/<int:participant_id>/', views.quiz_form, name='quiz_form'),
    path('submit_quiz/<int:participant_id>/', views.submit_quiz, name='submit_quiz'),
    path('certificate/<int:participant_id>/', views.generate_certificate, name='generate_certificate'),
    path('upload_profile/', views.upload_profile, name='upload_profile'),
    path('upload_cover/', views.upload_cover, name='upload_cover'),
    path('create_post/', views.create_post, name='create_post'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('add_audio_comment/<int:post_id>/', views.add_audio_comment, name='add_audio_comment'),
    path('login_view/', views.login_view, name='login_view'),
    path('reg_save/', views.reg_save, name='reg_save'),
    path('complaint/', views.complaint, name='complaint'),
    path('user_profile/<str:username>/', views.user_profile, name='user_profile'),
    path('logout/', views.logout, name='logout'),
    path('save_contact/', views.save_contact, name='save_contact'),
    path('save_complaint/', views.save_complaint, name='save_complaint'),
    path('chat/<str:room_name>/', views.chat_room, name='chat'),


]