from django.contrib import admin
from .models import *

class TamuAdmin(admin.ModelAdmin):
    list_display = ('nama', 'instansi', 'rand_code')
    list_filter = ('nama', 'instansi', 'rand_code')
    search_fields = ('nama', 'instansi')

class RegistrasiInline(admin.TabularInline):
    model = Registrasi
    extra = 1
    autocomplete_fields = ['tamu', 'meja']

class EventAdmin(admin.ModelAdmin):
    list_display = ('nama', 'tanggal', 'jam')
    search_fields = ('nama',)
    inlines = [RegistrasiInline]

class MejaAdmin(admin.ModelAdmin):
    list_display = ('nomor_meja', 'event')
    list_filter = ('event',)
    search_fields = ('nomor_meja',)

class RegistrasiAdmin(admin.ModelAdmin):
    list_display = ('event', 'tamu', 'meja', 'peserta', 'sudah_checkin')
    list_filter = ('event', 'sudah_checkin')
    search_fields = ('tamu__nama', 'tamu__instansi', 'peserta')
    autocomplete_fields = ['event', 'tamu', 'meja']

admin.site.register(Event, EventAdmin)
admin.site.register(Meja, MejaAdmin)
admin.site.register(Tamu, TamuAdmin)
admin.site.register(Registrasi, RegistrasiAdmin)
