from django.contrib import admin
from .models import *

class TamuAdmin(admin.ModelAdmin):
    list_display = ('nama', 'instansi', 'meja')

admin.site.register(Meja)
admin.site.register(Tamu, TamuAdmin)

