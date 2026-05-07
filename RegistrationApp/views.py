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
    success_url = '/'

class RegistrationLogoutView(LogoutView):
    template_name = 'login.html'
    next_page = '/'

class Scanner(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'scan.html'

class CheckInView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Tamu
    template_name = 'check_in_createview.html'
    fields = ['event', 'instansi', 'nama', 'meja', 'sudah_checkin']
    success_url = '../'

    def get_absolute_url(self):
        return reverse_lazy('checkin', kwargs={'slug':self.slug})

    def get_initial(self): #digunakan untuk memberikan nilai default di form    
        tamu = get_object_or_404(Tamu, slug=self.kwargs.get('slug'))
        #user = self.request.user.id
        return {
            'tamu':tamu,
        }
    
    def get_context_data(self, **kwargs): #digunakan untuk mengambil url dan mengirimkan nilainya ke template
        context = super().get_context_data(**kwargs)
        context['current_path'] = os.path.basename(self.request.get_full_path()) #digabung dengan fungsi os untuk mengambil url bagian terakhir saja
        context['path_without_query_string'] = self.request.path
        return context
    
class TamuListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Tamu
    template_name = 'tamu_listview.html'
    fields = '__all__'

def tamu_update_view(request):
    tamu_list = Tamu.objects.all().order_by('-sudah_checkin')
    return render(request, 'tamu_list_update.html', {'tamu_list': tamu_list})

class RegistrasiForm(forms.ModelForm):
    # Tambahkan field tambahan untuk profil tamu jika belum ada di master
    nama = forms.CharField(max_length=128)
    instansi = forms.CharField(max_length=128)

    class Meta:
        model = Registrasi
        fields = ['event', 'meja', 'sudah_checkin']

class TamuCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Registrasi
    form_class = RegistrasiForm
    template_name = 'tamu_form.html'
    success_url = reverse_lazy('list-tamu')

    def form_valid(self, form):
        # Logika: Cari Tamu berdasarkan nama/instansi, jika tidak ada buat baru
        nama = form.cleaned_data.pop('nama')
        instansi = form.cleaned_data.pop('instansi')
        tamu, created = Tamu.objects.get_or_create(
            nama=nama, 
            instansi=instansi
        )
        
        # Hubungkan pendaftaran dengan tamu tersebut
        form.instance.tamu = tamu
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

class MejaCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Meja
    template_name = 'meja_form.html'
    fields = ['nomor_meja']
    success_url = reverse_lazy('list-tamu')

class EventCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Event
    template_name = 'event_form.html'
    fields = ['nama', 'tanggal', 'jam', 'cover']
    success_url = reverse_lazy('list-tamu')

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
    success_url = reverse_lazy('list-tamu')

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
