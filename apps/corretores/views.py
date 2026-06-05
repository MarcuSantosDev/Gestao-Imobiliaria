from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.imoveis.models import Corretor

from .forms import CorretorForm


class CorretorListView(ListView):
    model = Corretor
    template_name = 'corretores/list.html'
    context_object_name = 'corretores'
    paginate_by = 10

    def get_queryset(self):
        qs = Corretor.objects.all()
        params = self.request.GET

        if q := params.get('q', '').strip():
            qs = qs.filter(
                Q(nome__icontains=q) | Q(telefone__icontains=q)
            )
        if tipo := params.get('tipo', '').strip():
            qs = qs.filter(tipo=tipo)

        return qs.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_choices'] = Corretor.TIPO_CHOICES
        return context


class CorretorCreateView(CreateView):
    model = Corretor
    form_class = CorretorForm
    template_name = 'corretores/form.html'
    success_url = reverse_lazy('corretores:list')


class CorretorUpdateView(UpdateView):
    model = Corretor
    form_class = CorretorForm
    template_name = 'corretores/form.html'
    success_url = reverse_lazy('corretores:list')


class CorretorDeleteView(DeleteView):
    model = Corretor
    template_name = 'corretores/confirm_delete.html'
    success_url = reverse_lazy('corretores:list')
