from django.contrib import admin
from .models import *

class TamuAdmin(admin.ModelAdmin):
    list_display = ('nama', 'instansi')

class RegistrasiAdmin(admin.ModelAdmin):
    list_display = ('event', 'tamu', 'meja', 'sudah_checkin')

admin.site.register(Event)
admin.site.register(Meja)
admin.site.register(Tamu, TamuAdmin)
admin.site.register(Registrasi, RegistrasiAdmin)
