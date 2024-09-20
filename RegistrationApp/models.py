from django.db import models

class Meja(model):
    nomor_meja = models.IntegerField()

class Tamu(models.Model):
    instansi = models.CharField(max_length=128)
    nama = models.CharField(max_length=128)
    meja = models.ForeignKey(Meja, on_delete=models.CASCADE)
