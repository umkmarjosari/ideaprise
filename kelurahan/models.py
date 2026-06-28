import os
from django.db import models
from django.dispatch import receiver
from kelurahan.utils import compress_image

class Kategori(models.Model):
    id_kategori = models.AutoField(primary_key=True)
    nama_kategori = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nama_kategori

class Kegiatan(models.Model):
    id_kegiatan = models.AutoField(primary_key=True)
    id_kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    nama_kegiatan = models.CharField(max_length=255, unique=True)
    gambar_kegiatan = models.ImageField(upload_to='images/kegiatan')
    deskripsi_kegiatan = models.TextField()

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.gambar_kegiatan:
                self.gambar_kegiatan = compress_image(self.gambar_kegiatan)
        else:
            try:
                orig = Kegiatan.objects.get(pk=self.pk)
                if orig.gambar_kegiatan != self.gambar_kegiatan and self.gambar_kegiatan:
                    self.gambar_kegiatan = compress_image(self.gambar_kegiatan)
            except Kegiatan.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama_kegiatan

class GambarKegiatan(models.Model):
    id_gambar = models.AutoField(primary_key=True)
    id_kegiatan = models.ForeignKey(Kegiatan, on_delete=models.CASCADE, related_name='gambar_tambahan')
    gambar = models.ImageField(upload_to='images/kegiatan/additional/')
    keterangan = models.CharField(max_length=255, blank=True, null=True)
    urutan = models.PositiveIntegerField(default=1)  # untuk mengurutkan gambar

    class Meta:
        ordering = ['urutan']

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.gambar:
                self.gambar = compress_image(self.gambar)
        else:
            try:
                orig = GambarKegiatan.objects.get(pk=self.pk)
                if orig.gambar != self.gambar and self.gambar:
                    self.gambar = compress_image(self.gambar)
            except GambarKegiatan.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_kegiatan.nama_kegiatan} - Gambar {self.urutan}"

class Produk(models.Model):
    id_produk = models.AutoField(primary_key=True)
    id_kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    nama_produk = models.CharField(max_length=255, unique=True)
    nomor_telepon = models.CharField(max_length=20)
    deskripsi_produk = models.TextField()
    gambar_produk = models.ImageField(upload_to='images/produk')
    thumbnail_produk = models.ImageField(upload_to='images/thumbnails', null=True, blank=True)
    link_shopee = models.URLField("Link Shopee", null=True, blank=True)
    link_tokopedia = models.URLField("Link Tokopedia", null=True, blank=True)
    harga_produk = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.gambar_produk:
                self.gambar_produk = compress_image(self.gambar_produk)
        else:
            try:
                orig = Produk.objects.get(pk=self.pk)
                if orig.gambar_produk != self.gambar_produk and self.gambar_produk:
                    self.gambar_produk = compress_image(self.gambar_produk)
            except Produk.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama_produk


class Bundling(models.Model):
    id_bundling = models.AutoField(primary_key=True)
    nama_bundling = models.CharField(max_length=255, unique=True)
    gambar_bundling = models.ImageField(upload_to='images/bundling')
    thumbnail_bundling = models.ImageField(upload_to='images/thumbnails', null=True, blank=True)
    harga_bundling = models.DecimalField(max_digits=10, decimal_places=2)
    link_shopee = models.URLField("Link Shopee", null=True, blank=True)
    link_tokopedia = models.URLField("Link Tokopedia", null=True, blank=True)
    deskripsi_bundling = models.TextField()

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.gambar_bundling:
                self.gambar_bundling = compress_image(self.gambar_bundling)
        else:
            try:
                orig = Bundling.objects.get(pk=self.pk)
                if orig.gambar_bundling != self.gambar_bundling and self.gambar_bundling:
                    self.gambar_bundling = compress_image(self.gambar_bundling)
            except Bundling.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama_bundling

class DetailBundling(models.Model):
    id_db = models.AutoField(primary_key=True)
    id_produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    id_bundling = models.ForeignKey(Bundling, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_bundling} - {self.id_produk}"


def _delete_files_for_instance(instance):
    file_fields = ['gambar_kegiatan', 'gambar', 'gambar_produk', 'thumbnail_produk', 'gambar_bundling', 'thumbnail_bundling']
    for field in file_fields:
        if hasattr(instance, field):
            file = getattr(instance, field)
            if file:
                try:
                    file.storage.delete(file.name)
                except Exception:
                    pass


@receiver(models.signals.post_delete, sender=Kegiatan)
def auto_delete_kegiatan_on_delete(sender, instance, **kwargs):
    _delete_files_for_instance(instance)

@receiver(models.signals.post_delete, sender=GambarKegiatan)
def auto_delete_gambarkegiatan_on_delete(sender, instance, **kwargs):
    _delete_files_for_instance(instance)

@receiver(models.signals.post_delete, sender=Produk)
def auto_delete_produk_on_delete(sender, instance, **kwargs):
    _delete_files_for_instance(instance)

@receiver(models.signals.post_delete, sender=Bundling)
def auto_delete_bundling_on_delete(sender, instance, **kwargs):
    _delete_files_for_instance(instance)
