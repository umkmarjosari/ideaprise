from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Kegiatan)
admin.site.register(models.Produk)
admin.site.register(models.Kategori)
admin.site.register(models.Bundling)
admin.site.register(models.DetailBundling)

