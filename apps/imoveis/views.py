from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Imovel
from .forms import ImovelForm

class ImovelListView(ListView):
    model = Imovel
    template_name = 'imoveis/list.html'
    context_object_name = 'imoveis'


class ImovelDetailView(DetailView):
    model = Imovel
    template_name = 'imoveis/detail.html'
    context_object_name = 'imovel'


class ImovelCreateView(CreateView):
    model = Imovel
    form_class = ImovelForm
    template_name = 'imoveis/form.html'
    success_url = reverse_lazy('imoveis:list')


class ImovelUpdateView(UpdateView):
    model = Imovel
    form_class = ImovelForm
    template_name = 'imoveis/form.html'
    success_url = reverse_lazy('imoveis:list')


class ImovelDeleteView(DeleteView):
    model = Imovel
    template_name = 'imoveis/confirm_delete.html'
    success_url = reverse_lazy('imoveis:list')