from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Gasto
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .forms import GastoForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import FormView
from .forms import RegistroUsuarioForm

# Create your views here.


@login_required
def dashboard(request):

    gastos = Gasto.objects.filter(
        usuario=request.user
    )  # "Obtenga los gastos cuyo usuario sea el usuario autenticado."

    resumen = gastos.aggregate(total=Sum("costo_real"), cantidad=Count("codigo"))

    context = {
        "total_gastos": resumen["total"] or 0,
        "cantidad_gastos": resumen["cantidad"] or 0,
    }

    return render(request, "gastos/dashboard.html", context)


class GastoListView(LoginRequiredMixin, ListView):

    model = Gasto
    template_name = "gastos/gasto_list.html"
    context_object_name = "gastos"

    def get_queryset(self):

        return Gasto.objects.filter(usuario=self.request.user)


class GastoCreateView(LoginRequiredMixin, CreateView):

    model = Gasto
    form_class = GastoForm
    template_name = "gastos/gasto_form.html"
    success_url = reverse_lazy("gasto_lista")

    def form_valid(self, form):

        form.instance.usuario = self.request.user

        return super().form_valid(form)


class GastoUpdateView(LoginRequiredMixin, UpdateView):

    model = Gasto
    form_class = GastoForm
    template_name = "gastos/gasto_form.html"
    success_url = reverse_lazy("gasto_lista")

    def get_queryset(self):

        return Gasto.objects.filter(usuario=self.request.user)


class GastoDeleteView(LoginRequiredMixin, DeleteView):

    model = Gasto
    template_name = "gastos/gasto_confirm_delete.html"
    success_url = reverse_lazy("gasto_lista")

    def get_queryset(self):

        return Gasto.objects.filter(usuario=self.request.user)


class RegistroView(FormView):

    template_name = "registration/registro.html"

    form_class = RegistroUsuarioForm

    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):

        usuario = form.save()

        login(self.request, usuario)

        return super().form_valid(form)
