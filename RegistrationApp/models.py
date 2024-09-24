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


class Meja(models.Model):
    nomor_meja = models.IntegerField()

    class Meta:
        verbose_name = 'Meja'
        verbose_name_plural = 'Meja'

    def __str__(self):
        return f"Meja nomor {self.nomor_meja} "

class Tamu(models.Model):
    instansi = models.CharField(max_length=128)
    nama = models.CharField(max_length=128, null=True, blank=True)
    meja = models.ForeignKey(Meja, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True)
    rand_code = models.CharField(max_length=8, unique=True, blank=True)
    slug = models.SlugField(max_length=8, blank=True)
    sudah_checkin = models.BooleanField()

    class Meta:
        verbose_name = 'Tamu'
        verbose_name_plural = 'Tamu'

    def __str__(self):
        return f"{self.instansi} {self.nama}"
    
    def save(self, *args, **kwargs):
        # Check if an old QR code exists and delete it
        if self.qr_code:
            file_path = self.qr_code.path #os.path.join(settings.MEDIA_ROOT, self.qr_code.path)
            logger.info(f'filepath: {file_path}')
            if os.path.exists(file_path):
                os.remove(file_path)

        #Buat QR Code nya
        qr_data = f"FLN_E01_{self.id}"
        qr_image = qrcode.make(self.rand_code)
        canvas = Image.new('RGB', (qr_image.size), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qr_image)

        #isi rand_code dan slug biar sama
        if not self.rand_code:
            self.rand_code = generate_random_number()
        if not self.slug:
            self.slug = slugify(self.rand_code)

        #Save ke memory
        buffer = BytesIO()
        canvas.save(buffer, format='PNG')
        file_name = f'qr_code_{self.instansi}_{self.nama}_{self.slug}.png'

        #Save ke DB
        self.qr_code.save(file_name, File(buffer), save=False)
        
        super().save(*args, **kwargs)

class CheckIn(models.Model):
    waktu = models.DateTimeField(auto_now_add=True)
    tamu = models.ForeignKey(Tamu, on_delete=models.CASCADE)