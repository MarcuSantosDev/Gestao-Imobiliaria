import json

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from apps.imoveis.localidades import BAIRROS
from apps.imoveis.mixins import LocalidadesFormMixin
from apps.imoveis.models import DemandaCliente

from .forms import DemandaForm
from .matching import buscar_imoveis_compativeis


class DemandaListView(ListView):
    model = DemandaCliente
    template_name = 'demandas/list.html'
    context_object_name = 'demandas'

    def get_queryset(self):
        qs = super().get_queryset().select_related('cliente')
        busca = self.request.GET.get('q', '').strip()
        if busca:
            qs = qs.filter(cliente__nome__icontains=busca)
        return qs.order_by('-criado_em')


class DemandaDetailView(DetailView):
    model = DemandaCliente
    template_name = 'demandas/detail.html'
    context_object_name = 'demanda'


class DemandaFormMixin(LocalidadesFormMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object and self.object.pk:
            context['bairros_selecionados_json'] = json.dumps(self.object.get_bairros_lista())
        return context


class DemandaCreateView(DemandaFormMixin, CreateView):
    model = DemandaCliente
    form_class = DemandaForm
    template_name = 'demandas/form.html'
    success_url = reverse_lazy('demandas:list')


class DemandaUpdateView(DemandaFormMixin, UpdateView):
    model = DemandaCliente
    form_class = DemandaForm
    template_name = 'demandas/form.html'
    success_url = reverse_lazy('demandas:list')


class DemandaDeleteView(DeleteView):
    model = DemandaCliente
    template_name = 'demandas/confirm_delete.html'
    success_url = reverse_lazy('demandas:list')


class DemandaBuscaView(DetailView):
    model = DemandaCliente
    template_name = 'demandas/busca.html'
    context_object_name = 'demanda'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resultados'] = buscar_imoveis_compativeis(self.object)
        return context


class DemandaAtenderView(View):
    def post(self, request, pk):
        demanda = get_object_or_404(DemandaCliente, pk=pk)
        demanda.status = 'atendida'
        demanda.save()
        messages.success(request, 'Demanda marcada como atendida.')
        return redirect('demandas:detail', pk=pk)
