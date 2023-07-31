from django.urls import path
from . import views

app_name = 'ayou'
urlpatterns = [
    path('', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('logout/', views.logout_view , name='logout'),
    path('chat/', views.chat, name='chat'),
    path('memories/', views.memories, name='memories'),
    

    path('social/', views.social, name='social'),
    path('account/', views.account, name='account')
]