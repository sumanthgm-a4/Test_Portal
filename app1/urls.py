from django.urls import path
from .views import *

urlpatterns = [
    path("", render_home, name="home"),
    path("login", render_login, name="login"),
    path("register", render_register, name="register"),
    path("logout", render_logout, name="logout"),
]