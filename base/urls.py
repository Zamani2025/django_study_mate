from django.urls import path
from . import views



urlpatterns = [
    path('login/', view=views.loginPage, name="login"),
    path('logout/', view=views.logoutUser, name="logout"),
    path('register/', view=views.registerPage, name="register"),

    path('', view=views.home, name="home"),
    path('room/<str:pk>/', view=views.room, name="room"),
    path('activities/', view=views.activityPage, name="activity"),
    path('topics/', view=views.topicPage, name="topic"),
    path('profile/<str:pk>/', view=views.userProfile, name="profile"),
    path('edit-user/', view=views.updateUser, name="updateUser"),

    path('create-room', view=views.createRoom, name='create_room'),
    path('update-room/<str:pk>/', view=views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', view=views.deleteRoom, name='delete-room'),
    path('delete-message/<str:pk>/', view=views.deleteMessage, name='delete-message')
]