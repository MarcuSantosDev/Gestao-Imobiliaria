from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from apps.imoveis.models import Corretor
from .forms import CorretorForm

class CorretorListView(ListView):
    model = Corretor
    template_name = 'corretores/list.html'
    context_object_name = 'corretores'


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