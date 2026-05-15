from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import random
import os
from django.conf import settings
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

def generate_random_number():
    return random.randrange(10000000, 100000000)

def get_qr_code_upload_path(instance, filename):
    # This will create a path: 'qr_codes/qr_code_<name>.png'
    return os.path.join('qr_codes')#, f'qr_code_{instance.instansi}_{instance.nama}.png')

class Event(models.Model):
    nama = models.CharField(max_length=255)
    tanggal = models.DateField()
    jam = models.TimeField()
    cover = models.ImageField(upload_to='event_covers/', blank=True, null=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Event'

    def __str__(self):
        return self.nama

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.cover:
            img = Image.open(self.cover.path)
            # Memastikan ukuran 400x400 menggunakan metode resize
            if img.height != 400 or img.width != 400:
                output_size = (400, 400)
                img = img.resize(output_size, Image.LANCZOS)
                img.save(self.cover.path)

class Meja(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    nomor_meja = models.IntegerField()


    class Meta:
        verbose_name = 'Meja'
        verbose_name_plural = 'Meja'

    def __str__(self):
        return f"Meja nomor {self.nomor_meja} "

class Tamu(models.Model):
    instansi = models.CharField(max_length=128, null=True, blank=True)
    nama = models.CharField(max_length=128, null=True, blank=True)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True)
    rand_code = models.CharField(max_length=8, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=8, blank=True, null=True)

    class Meta:
        verbose_name = 'Tamu'
        verbose_name_plural = 'Tamu'
        unique_together = ('nama', 'instansi')

    def __str__(self):
        return f"{self.instansi} {self.nama}"

    def save(self, *args, **kwargs):
        # Hapus file QR lama jika ada perubahan (opsional)
        if self.pk:
            old_obj = Tamu.objects.filter(pk=self.pk).first()
            if old_obj and old_obj.qr_code and old_obj.qr_code != self.qr_code:
                if os.path.exists(old_obj.qr_code.path):
                    os.remove(old_obj.qr_code.path)

        # Isi rand_code dan slug jika belum ada
        if not self.rand_code:
            self.rand_code = str(generate_random_number())
        if not self.slug:
            self.slug = slugify(self.rand_code)

        # Buat QR Code (Hanya jika belum memiliki file qr_code)
        if not self.qr_code:
            qr_image = qrcode.make(self.rand_code)
            canvas = Image.new('RGB', (qr_image.size), 'white')
            canvas.paste(qr_image)

            buffer = BytesIO()
            canvas.save(buffer, format='PNG')
            file_name = f'qr_tamu_{self.slug}.png'

            self.qr_code.save(file_name, File(buffer), save=False)
        
        super().save(*args, **kwargs)

class Registrasi(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='pendaftaran_list')
    tamu = models.ForeignKey(Tamu, on_delete=models.CASCADE, related_name='riwayat_event')
    meja = models.ForeignKey(Meja, on_delete=models.CASCADE, null=True, blank=True)
    peserta = models.TextField(blank=True, null=True, verbose_name="Daftar Peserta Tambahan")
    sudah_checkin = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Pendaftaran'
        verbose_name_plural = 'Pendaftaran'
        unique_together = ('event', 'tamu')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class CheckIn(models.Model):
    waktu = models.DateTimeField(auto_now_add=True)
    pendaftaran = models.ForeignKey(Registrasi, on_delete=models.CASCADE)