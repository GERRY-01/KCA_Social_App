from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('complete_profile/', views.complete_profile, name='complete_profile'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('create_post/', views.create_post, name='create_post'),
    path('profile/', views.profile, name='profile'),
    path('post/<int:post_id>/add_comment/', views.add_comment, name='add_comment'),
    path('suggestions/', views.view_all_suggestions, name='suggestions'),
    path('resources', views.resources, name='resources'),
    path('events', views.events, name='events'),
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/like/<int:announcement_id>/', views.like_announcement, name='like_announcement'),
    path('announcements/delete/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),
    path('announcements/edit/<int:announcement_id>/', views.edit_announcement, name='edit_announcement'),
    path('admin_signup', views.admin_signup, name='admin_signup'),
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('accept_follow/<int:user_id>/', views.accept_follow, name='accept_follow'),
    path('decline_follow/<int:user_id>/', views.decline_follow, name='decline_follow'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('update_profile/', views.update_profile, name='update_profile'),
]