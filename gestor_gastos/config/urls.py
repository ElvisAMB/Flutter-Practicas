from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from gastos.views import RegistroView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login",),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('registro/', RegistroView.as_view(), name='registro'),
    path("", include("gastos.urls")),
]
