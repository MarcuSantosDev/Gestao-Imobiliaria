from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.imoveis.models import Cliente

from .forms import ClienteForm


class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes/list.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        qs = Cliente.objects.all()
        params = self.request.GET

        if q := params.get('q', '').strip():
            qs = qs.filter(
                Q(nome__icontains=q) | Q(email__icontains=q)
            )
        if telefone := params.get('telefone', '').strip():
            qs = qs.filter(telefone__icontains=telefone)

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
