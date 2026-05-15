from django.shortcuts import render
from django import forms
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from .models import *
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
import os
import logging

logger = logging.getLogger(__name__)

redirect_authenticated_user = True

class RegistrationLoginView(LoginView):
    template_name = 'login.html'
    success_url = 'event-list'

class RegistrationLogoutView(LogoutView):
    template_name = 'login.html'
    next_page = 'event-list'

class Scanner(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'scan.html'

class CheckInView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Registrasi
    template_name = 'check_in_createview.html'
    fields = ['sudah_checkin']
    success_url = '../'
    
    def get_object(self, queryset=None):
        # Cari registrasi berdasarkan slug yang sekarang ada di model Tamu
        # Mengambil registrasi terbaru (misal: event dengan tanggal paling baru)
        obj = Registrasi.objects.select_related('tamu', 'event').filter(
            tamu__slug=self.kwargs['slug']
        ).order_by('-event__tanggal').first()
        
        if not obj:
            raise Http404("Data pendaftaran tidak ditemukan.")
        return obj

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ini akan memaksa checkbox jadi True saat halaman edit dibuka,
        # meskipun di database sebelumnya nilainya False.
        form.initial['sudah_checkin'] = True
        form.fields['sudah_checkin'].widget = forms.HiddenInput()
        form.fields['sudah_checkin'].label = ""
        return form

    def get_initial(self): #digunakan untuk memberikan nilai default di form    
        return super().get_initial()
    
    def get_context_data(self, **kwargs): #digunakan untuk mengambil url dan mengirimkan nilainya ke template
        context = super().get_context_data(**kwargs)
        context['current_path'] = os.path.basename(self.request.get_full_path()) #digabung dengan fungsi os untuk mengambil url bagian terakhir saja
        context['path_without_query_string'] = self.request.path
        return context
    
class TamuListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Registrasi
    template_name = 'tamu_listview.html'
    context_object_name = 'tamu_list'

class TamuEditListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Registrasi
    template_name = 'tamu_list_edit.html'
    context_object_name = 'tamu_list_edit'

def tamu_update_view(request):
    tamu_list = Registrasi.objects.all().select_related('tamu', 'meja').order_by('-sudah_checkin')
    return render(request, 'tamu_list_update.html', {'tamu_list': tamu_list})

class RegistrasiForm(forms.ModelForm):
    # Field untuk memilih tamu yang sudah ada agar tidak perlu input ulang
    tamu = forms.ModelChoiceField(
        queryset=Tamu.objects.all(),
        required=False,
        label="Pilih Tamu (Kosongkan jika tamu baru)",
        empty_label="--- Pilih Tamu yang Sudah Ada ---"
    )
    nama = forms.CharField(max_length=128, required=False, label="Nama (Tamu Baru)")
    instansi = forms.CharField(max_length=128, required=False, label="Instansi (Tamu Baru)")

    class Meta:
        model = Registrasi
        fields = ['event', 'tamu', 'meja', 'peserta', 'sudah_checkin']

    def clean(self):
        cleaned_data = super().clean()
        tamu = cleaned_data.get('tamu')
        nama = cleaned_data.get('nama')
        instansi = cleaned_data.get('instansi')
        event = cleaned_data.get('event')

        if not tamu and (not nama or not instansi):
            raise forms.ValidationError("Pilih tamu dari daftar atau masukkan data tamu baru (Nama & Instansi).")

        # Cek apakah tamu sudah terdaftar di event ini (baik melalui pilihan dropdown atau input manual)
        check_tamu = tamu or Tamu.objects.filter(nama=nama, instansi=instansi).first()
        if check_tamu and event:
            qs = Registrasi.objects.filter(event=event, tamu=check_tamu)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"Tamu ini sudah terdaftar di event {event.nama}.")
            
        return cleaned_data

class TamuCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Registrasi
    form_class = RegistrasiForm
    template_name = 'tamu_form.html'
    success_url = reverse_lazy('list-tamu')

    def form_valid(self, form):
        # Jika tamu tidak dipilih dari dropdown, cari atau buat berdasarkan input manual
        if not form.cleaned_data.get('tamu'):
            nama = form.cleaned_data.get('nama')
            instansi = form.cleaned_data.get('instansi')
            tamu, created = Tamu.objects.get_or_create(
                nama=nama, 
                instansi=instansi
            )
            form.instance.tamu = tamu
        # Pastikan tamu memiliki slug (terutama untuk data lama yang diambil dari dropdown)
        if form.instance.tamu and not form.instance.tamu.slug:
            form.instance.tamu.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        event_id = self.kwargs.get('event_id')
        if event_id:
            initial['event'] = get_object_or_404(Event, pk=event_id)
        initial['sudah_checkin'] = False
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.kwargs.get('event_id'):
            # Membuat field event tidak bisa diubah
            form.fields['event'].disabled = True
        # Membuat field sudah_checkin menjadi hidden
        # Membuat field sudah_checkin menjadi hidden dan menyembunyikan labelnya
        form.fields['sudah_checkin'].widget = forms.HiddenInput()
        form.fields['sudah_checkin'].label = ""
        return form

    def get_success_url(self):
        event_id = self.kwargs.get('event_id')
        if event_id:
            return reverse_lazy('event-detail', kwargs={'pk': event_id})
        return self.success_url
    
class TamuUpdateView(LoginRequiredMixin, UpdateView):
    model = Registrasi
    form_class = RegistrasiForm
    template_name = 'tamu_form.html'
    success_url = reverse_lazy('list-tamu-edit')

    def get_initial(self):
        initial = super().get_initial()
        # Ambil data nama dan instansi dari objek Tamu terkait untuk ditampilkan di form
        if self.object.tamu:
            initial['nama'] = self.object.tamu.nama
            initial['instansi'] = self.object.tamu.instansi
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Saat update, kunci field event dan sembunyikan field tamu/checkin
        form.fields['event'].disabled = True
        form.fields['tamu'].widget = forms.HiddenInput()
        form.fields['sudah_checkin'].widget = forms.HiddenInput()
        form.fields['sudah_checkin'].label = ""
        return form

    def form_valid(self, form):
        # Simpan perubahan Nama & Instansi langsung ke objek Tamu (Master Data)
        tamu = self.object.tamu
        tamu.nama = form.cleaned_data.get('nama')
        tamu.instansi = form.cleaned_data.get('instansi')
        tamu.save()
        return super().form_valid(form)


class MejaCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Meja
    template_name = 'meja_form.html'
    fields = ['event', 'nomor_meja']
    success_url = reverse_lazy('meja-list')

class MejaListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Meja
    template_name = 'meja_list.html'
    context_object_name = 'meja_list'


class EventCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Event
    template_name = 'event_form.html'
    fields = ['nama', 'tanggal', 'jam', 'cover']
    success_url = reverse_lazy('event-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tanggal'].widget = forms.DateInput(
            format='%Y-%m-%d', 
            attrs={'type': 'date', 'class': 'form-control'}
        )
        form.fields['jam'].widget = forms.TimeInput(
            format='%H:%M', 
            attrs={'type': 'time', 'class': 'form-control'}
        )
        return form

class EventUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Event
    template_name = 'event_form.html'
    fields = ['nama', 'tanggal', 'jam', 'cover']
    success_url = reverse_lazy('event-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tanggal'].widget = forms.DateInput(
            format='%Y-%m-%d', 
            attrs={'type': 'date', 'class': 'form-control'}
        )
        form.fields['jam'].widget = forms.TimeInput(
            format='%H:%M', 
            attrs={'type': 'time', 'class': 'form-control'}
        )
        return form

class EventListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Event
    template_name = 'event_list.html'
    context_object_name = 'events'
    ordering = ['-tanggal', '-jam']

class EventDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'
