from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw

class Meja(models.Model):
    nomor_meja = models.IntegerField()

    class Meta:
        verbose_name = 'Meja'
        verbose_name_plural = 'Meja'

    def __str__(self):
        return f"Meja nomor {self.nomor_meja} "

class Tamu(models.Model):
    instansi = models.CharField(max_length=128)
    nama = models.CharField(max_length=128)
    meja = models.ForeignKey(Meja, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    class Meta:
        verbose_name = 'Tamu'
        verbose_name_plural = 'Tamu'

    def __str__(self):
        return f"{self.nama} {self.instansi}"
    
    def save(self, *args, **kwargs):
        #Buat QR Code nya
        qr_image = qrcode.make(self.url)
        canvas = Image.new('RGB', (qr_image.pixel_size), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qr_image)

        #Save ke memory
        buffer = BytesIO()
        canvas.save(buffer, format='PNG')
        file_name = f'qr_code_{self.nama}.png'

        #Save ke DB
        self.qr_code.save(file_name, File(bufer), save=False)
        super().save(*args, **kwargs)