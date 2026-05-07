from django.contrib import admin
from .models import *

class TamuAdmin(admin.ModelAdmin):
    list_display = ('nama', 'instansi', 'meja', 'event')

admin.site.register(Event)
admin.site.register(Meja)
admin.site.register(Tamu, TamuAdmin)
