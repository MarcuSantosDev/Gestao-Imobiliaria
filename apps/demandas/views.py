import json

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
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
        qs = DemandaCliente.objects.filter(status='aberta').select_related('cliente')
        busca = self.request.GET.get('q', '').strip()
        if busca:
            qs = qs.filter(cliente__nome__icontains=busca)
        return qs.order_by('-criado_em')


class DemandaDetailView(DetailView):
    model = DemandaCliente
    template_name = 'demandas/detail.html'
    context_object_name = 'demanda'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status == 'atendida':
            messages.info(request, 'Esta demanda já foi finalizada e está no histórico.')
            return redirect('historico:demandas')
        return super().get(request, *args, **kwargs)


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

    def get_queryset(self):
        return DemandaCliente.objects.filter(status='aberta')

    def form_valid(self, form):
        self.object = form.save()
        if self.object.status == 'atendida':
            messages.success(self.request, 'Demanda finalizada e movida para o histórico.')
            return redirect('historico:demandas')
        messages.success(self.request, 'Demanda atualizada com sucesso.')
        return redirect(self.success_url)


class DemandaDeleteView(DeleteView):
    model = DemandaCliente
    template_name = 'demandas/confirm_delete.html'
    success_url = reverse_lazy('demandas:list')

    def get_queryset(self):
        return DemandaCliente.objects.filter(status='aberta')


class DemandaBuscaView(DetailView):
    model = DemandaCliente
    template_name = 'demandas/busca.html'
    context_object_name = 'demanda'

    def get_queryset(self):
        return DemandaCliente.objects.filter(status='aberta')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resultados'] = buscar_imoveis_compativeis(self.object)
        return context


class DemandaAtenderView(View):
    def post(self, request, pk):
        demanda = get_object_or_404(DemandaCliente, pk=pk, status='aberta')
        demanda.status = 'atendida'
        demanda.atendida_em = timezone.now()
        demanda.save()
        messages.success(request, 'Demanda finalizada e movida para o histórico.')
        return redirect('historico:demandas')
