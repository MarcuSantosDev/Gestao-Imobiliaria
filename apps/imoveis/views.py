import io
import os
import zipfile

from django.http import JsonResponse
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from .forms import ImovelForm
from .mixins import LocalidadesFormMixin
from .models import FotoImovel, Imovel
from .sharing import gerar_texto_compartilhamento


class ImovelListView(ListView):
    model = Imovel
    template_name = 'imoveis/list.html'
    context_object_name = 'imoveis'

    def get_queryset(self):
        qs = super().get_queryset().select_related('categoria', 'corretor').prefetch_related('fotos')
        busca = self.request.GET.get('q', '').strip()
        if busca:
            qs = qs.filter(titulo__icontains=busca)
        return qs.order_by('-id')


class ImovelDetailView(DetailView):
    model = Imovel
    template_name = 'imoveis/detail.html'
    context_object_name = 'imovel'

    def get_queryset(self):
        return super().get_queryset().select_related('categoria', 'corretor').prefetch_related(
            'fotos', 'infraestrutura'
        )


class ImovelCreateView(LocalidadesFormMixin, CreateView):
    model = Imovel
    form_class = ImovelForm
    template_name = 'imoveis/form.html'
    success_url = reverse_lazy('imoveis:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self._salvar_fotos(self.object)
        return response

    def _salvar_fotos(self, imovel):
        for foto in self.request.FILES.getlist('fotos'):
            FotoImovel.objects.create(imovel=imovel, imagem=foto)


class ImovelUpdateView(LocalidadesFormMixin, UpdateView):
    model = Imovel
    form_class = ImovelForm
    template_name = 'imoveis/form.html'
    success_url = reverse_lazy('imoveis:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self._salvar_fotos(self.object)
        return response

    def _salvar_fotos(self, imovel):
        for foto in self.request.FILES.getlist('fotos'):
            FotoImovel.objects.create(imovel=imovel, imagem=foto)


class ImovelDeleteView(DeleteView):
    model = Imovel
    template_name = 'imoveis/confirm_delete.html'
    success_url = reverse_lazy('imoveis:list')


class ImovelCompartilharTextoView(View):
    def get(self, request, pk):
        imovel = Imovel.objects.select_related('corretor').prefetch_related('infraestrutura').get(pk=pk)
        return JsonResponse({'texto': gerar_texto_compartilhamento(imovel)})


class ImovelCompartilharFotosView(View):
    def get(self, request, pk):
        imovel = Imovel.objects.prefetch_related('fotos').get(pk=pk)
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, foto in enumerate(imovel.fotos.all(), start=1):
                if foto.imagem:
                    ext = os.path.splitext(foto.imagem.name)[1] or '.jpg'
                    zf.writestr(f'foto_{i}{ext}', foto.imagem.read())

        nome_arquivo = f"{imovel.titulo.replace(' ', '_')}.zip"
        response = HttpResponse(buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        return response
