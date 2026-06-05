from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from apps.imoveis.models import Cliente
from .forms import ClienteForm

class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes/list.html'
    context_object_name = 'clientes'

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get('q', '').strip()
        if busca:
            qs = qs.filter(nome__icontains=busca)
        return qs.order_by('-criado_em')


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes:list')


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes:list')


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'clientes/confirm_delete.html'
    success_url = reverse_lazy('clientes:list')