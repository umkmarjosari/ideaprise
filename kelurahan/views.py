from django.shortcuts import render, redirect
from . import models
from datetime import datetime
import calendar
from .decorators import role_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login , logout, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.forms import DateInput
from django.db.models import F,Q,Sum,Value
import math
from django.template.loader import render_to_string
import tempfile
from django.urls import reverse  
from django.db.models import Count  
from django.utils import timezone
from django.db.models import Count
from . import models
from django.shortcuts import get_object_or_404, redirect
from django import forms
from .models import Kategori, Kegiatan, Produk, Bundling, DetailBundling, GambarKegiatan
import base64
from django.core.files.base import ContentFile
import numpy as np



def base(request):
    kegiatanobj = Kegiatan.objects.all()
    return render(request, 'base/base.html', {'kegiatanobj': kegiatanobj})

def loginview(request):
    if request.user.is_authenticated:
        return redirect('base')  # atau dashboard kamu

    return render(request, 'base/login.html')  # tampilkan form login

def performlogin(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed")
    else:
        username_login = request.POST['username']
        password_login = request.POST['password']
        userobj = authenticate(request, username=username_login, password=password_login)
        
        if userobj is not None:
            login(request, userobj)
            messages.success(request, "Login success")
            
            if userobj.groups.filter(name='admin').exists():
                return redirect("base")
            else :
                return redirect("base")
            
        else:
            messages.error(request, "Username atau Password salah !!!")
            return redirect("login")
        
@login_required(login_url="login")
def logoutview(request):
    logout(request)
    messages.info(request,"Berhasil Logout")
    return redirect('login')

@login_required(login_url="login")
def performlogout(request):
    logout(request)
    return redirect("login")

# CRUD DATA KATEGORI 
@login_required(login_url="login")
@role_required(['admin']) 
def create_kategori(request):
    if request.method == 'GET':
        return render(request, 'kategori/create_kategori.html')
    else:
        nk = request.POST.get('nama_kategori') #yang kanan harus sesuai name di html
        if not nk:
            messages.error(request, 'Nama kategori tidak boleh kosong!')
            return render(request, 'kategori/create_kategori.html', {'old_data': request.POST})

        kategoriobj = Kategori.objects.filter(nama_kategori=nk) 

        if kategoriobj.exists():
            messages.error(request, 'Kategori ini sudah ada!')
            return render(request, 'kategori/create_kategori.html', {'old_data': request.POST})
        else:
            Kategori(
                nama_kategori= nk,
            ).save()
            messages.success(request, 'Data kategori berhasil ditambahkan!')

        return redirect('read_kategori')

def read_kategori(request):
    kategoriobj = models.Kategori.objects.all()
    if not kategoriobj.exists():
        messages.error(request, "Data kategori tidak ditemukan!")
        return render(request, 'kategori/read_kategori.html', {'kategoriobj': None})
    else:
        return render(request, 'kategori/read_kategori.html', {'kategoriobj': kategoriobj})

@login_required(login_url="login")
@role_required(['admin']) 
def update_kategori(request, id):
    # kategoriobj = Kategori.objects.all()
    try:
        getkategori = Kategori.objects.get(id_kategori=id)  
    except Kategori.DoesNotExist:
        messages.error(request, 'Kategori tidak ditemukan.')
        return redirect('read_kategori')

    if request.method == 'GET':
        return render(request, 'kategori/update_kategori.html', {'getkategori': getkategori})
    
    else:
        nk = request.POST.get('nama_kategori') #yang kanan harus sesuai name di html
        
        if not nk:
            messages.error(request, 'Nama kategori tidak boleh kosong!')
            return render(request, 'kategori/update_kategori.html', {'getkategori': getkategori, 'old_data': request.POST})
            
        cekkategorikak = Kategori.objects.filter(nama_kategori=nk).exclude(id_kategori=id) #ngefilter kolom database nama produk berdasarkan np yg diinput user kecuali nama produknya sendiri berdasarkan id
        
        if cekkategorikak.exists(): #cek apakah ada produk lain dgn nama produk yg diupdate 
            messages.error(request, 'Kategori ini sudah ada!')
            return render(request, 'kategori/update_kategori.html', {'getkategori': getkategori, 'old_data': request.POST}) #pake parameter id karena html update b/o id 

        getkategori.nama_kategori = nk #di savenya bukan ke models produk krn yg diperbarui data produk per id yg mana query data produk per id udh didefinisikan di var getproduk sblmnya
        getkategori.save()
        
        return redirect("read_kategori")

@login_required(login_url="login")
@role_required(['admin']) 
def delete_kategori(request, id):
    try:
        getkategori = Kategori.objects.get(id_kategori=id)  
        getkategori.delete()
        
        messages.success(request, "Data kategori berhasil dihapus!")  
    except Kategori.DoesNotExist:
        messages.error(request, "Kategori tidak ditemukan.")
    
    return redirect('read_kategori')


# CRUD DATA KEGIATAN dengan multiple images
@login_required(login_url="login")
@role_required(['admin']) 
def create_kegiatan(request):
    kategoriobj = Kategori.objects.all()
    if request.method == 'GET':
        return render(request, 'kegiatan/create_kegiatan.html',{'kategoriobj':kategoriobj})
    else:
        idk = request.POST.get('id_kategori')
        nkn = request.POST.get('nama_kegiatan')
        gk = request.FILES.get('gambar_kegiatan')
        dk = request.POST.get('deskripsi_kegiatan')
        
        # Ambil multiple images
        gambar_tambahan = request.FILES.getlist('gambar_tambahan')
        keterangan_gambar = request.POST.getlist('keterangan_gambar')

        kegiatanobj = Kegiatan.objects.filter(nama_kegiatan=nkn) 
        
        try:
            datakategori = Kategori.objects.get(id_kategori = idk)
        except (Kategori.DoesNotExist, ValueError):
            messages.error(request, "Kategori tidak ditemukan atau tidak valid.")
            return render(request, 'kegiatan/create_kegiatan.html', {'kategoriobj': Kategori.objects.all(), 'old_data': request.POST})

        if kegiatanobj.exists():
            messages.error(request, 'Kegiatan ini sudah ada!')
            return render(request, 'kegiatan/create_kegiatan.html', {'kategoriobj': Kategori.objects.all(), 'old_data': request.POST})
        else:
            # Simpan kegiatan utama
            kegiatan_baru = Kegiatan(
                id_kategori = datakategori,
                nama_kegiatan = nkn,
                gambar_kegiatan = gk,
                deskripsi_kegiatan = dk
            )
            kegiatan_baru.save()
            
            # Simpan gambar tambahan
            for i, gambar in enumerate(gambar_tambahan):
                keterangan = keterangan_gambar[i] if i < len(keterangan_gambar) else ''
                GambarKegiatan.objects.create(
                    id_kegiatan=kegiatan_baru,
                    gambar=gambar,
                    keterangan=keterangan,
                    urutan=i+1
                )
            
            messages.success(request, 'Data kegiatan berhasil ditambahkan!')

        return redirect('read_kegiatan')

def read_kegiatan(request):
    # Prefetch gambar_tambahan untuk efisiensi query
    kegiatanobj = Kegiatan.objects.prefetch_related('gambar_tambahan').all()
    if not kegiatanobj.exists():
        messages.error(request, "Data kegiatan tidak ditemukan!")
        return render(request, 'kegiatan/read_kegiatan.html', {'kegiatanobj': None})
    else:
        return render(request, 'kegiatan/read_kegiatan.html', {'kegiatanobj': kegiatanobj})

@login_required(login_url="login")
@role_required(['admin']) 
def update_kegiatan(request, id):
    getkegiatan = get_object_or_404(Kegiatan,id_kegiatan=id)
    gambar_lama = getkegiatan.gambar_kegiatan
    kategoriobj = Kategori.objects.all()
    gambar_tambahan_existing = GambarKegiatan.objects.filter(id_kegiatan=getkegiatan)

    if request.method == 'GET':
        return render(request, 'kegiatan/update_kegiatan.html', {
            'getkegiatan': getkegiatan,
            'kategoriobj': kategoriobj,
            'gambar_tambahan': gambar_tambahan_existing
        })
    
    else:
        idk = request.POST.get('id_kategori')
        nkn = request.POST.get('nama_kegiatan')
        gk = request.FILES.get('gambar_kegiatan')
        dk = request.POST.get('deskripsi_kegiatan')
        
        # Ambil data gambar tambahan
        gambar_tambahan_baru = request.FILES.getlist('gambar_tambahan_baru')
        keterangan_baru = request.POST.getlist('keterangan_gambar_baru')
        hapus_gambar = request.POST.getlist('hapus_gambar')

        cekkegiatankak = Kegiatan.objects.filter(nama_kegiatan=nkn).exclude(id_kegiatan=id)
        
        try:
            datakategori = Kategori.objects.get(id_kategori = idk)
        except (Kategori.DoesNotExist, ValueError):
            messages.error(request, "Kategori tidak ditemukan atau tidak valid.")
            return render(request, 'kegiatan/update_kegiatan.html', {
                'getkegiatan': getkegiatan, 'kategoriobj': Kategori.objects.all(),
                'gambar_tambahan_existing': GambarKegiatan.objects.filter(id_kegiatan=getkegiatan),
                'old_data': request.POST
            })

        if cekkegiatankak.exists():
            messages.error(request, 'Kegiatan ini sudah ada!')
            return render(request, 'kegiatan/update_kegiatan.html', {
                'getkegiatan': getkegiatan, 'kategoriobj': Kategori.objects.all(),
                'gambar_tambahan_existing': GambarKegiatan.objects.filter(id_kegiatan=getkegiatan),
                'old_data': request.POST
            })

        getkegiatan.id_kategori = datakategori
        getkegiatan.nama_kegiatan = nkn
        getkegiatan.deskripsi_kegiatan = dk

        if gk:
            getkegiatan.gambar_kegiatan = gk
        else:
            getkegiatan.gambar_kegiatan = gambar_lama
    
        getkegiatan.save()
        
        # Hapus gambar yang dipilih untuk dihapus
        for gambar_id in hapus_gambar:
            try:
                gambar_obj = GambarKegiatan.objects.get(id_gambar=gambar_id)
                gambar_obj.delete()
            except GambarKegiatan.DoesNotExist:
                pass
        
        # Tambah gambar baru
        urutan_terakhir = GambarKegiatan.objects.filter(id_kegiatan=getkegiatan).count()
        for i, gambar in enumerate(gambar_tambahan_baru):
            keterangan = keterangan_baru[i] if i < len(keterangan_baru) else ''
            GambarKegiatan.objects.create(
                id_kegiatan=getkegiatan,
                gambar=gambar,
                keterangan=keterangan,
                urutan=urutan_terakhir + i + 1
            )
        
        messages.success(request, 'Data kegiatan berhasil diperbarui!')
        return redirect("read_kegiatan")
    
def read_detailkegiatan(request, id):
    try:
        getkegiatan = Kegiatan.objects.get(id_kegiatan=id)
        gambar_tambahan = GambarKegiatan.objects.filter(id_kegiatan=getkegiatan)
        return render(request, 'kegiatan/read_detailkegiatan.html', {
            'getkegiatan': getkegiatan,
            'gambar_tambahan': gambar_tambahan
        })
    except Kegiatan.DoesNotExist:
        messages.error(request, 'Kegiatan tidak ditemukan.')
        return redirect('read_kegiatan')
    
@login_required(login_url="login")
@role_required(['admin']) 
def delete_kegiatan(request, id):
    try:
        getkegiatan = Kegiatan.objects.get(id_kegiatan=id)  
        getkegiatan.delete()  # Ini akan otomatis menghapus gambar tambahan karena CASCADE
        
        messages.success(request, "Data kegiatan berhasil dihapus!")  
    except Kegiatan.DoesNotExist:
        messages.error(request, "Kegiatan tidak ditemukan.")
    
    return redirect('read_kegiatan')

# CRUD DATA PRODUK 
@login_required(login_url="login")
@role_required(['admin']) 
def create_produk(request):
    kategoriobj = Kategori.objects.all()

    if request.method == 'GET':
        return render(request, 'produk/create_produk.html', {'kategoriobj': kategoriobj})
    
    else:
        idk = request.POST.get('id_kategori')
        np = request.POST.get('nama_produk')
        nt = request.POST.get('nomor_telepon')
        dp = request.POST.get('deskripsi_produk')
        gp = request.FILES.get('gambar_produk')
        link_shopee = request.POST.get('link_shopee') or ''
        link_tokopedia = request.POST.get('link_tokopedia') or ''
        hp = request.POST.get('harga_produk')
        tb64 = request.POST.get('thumbnail_base64')

        # Cek apakah produk sudah ada
        if Produk.objects.filter(nama_produk=np).exists():
            messages.error(request, 'Produk ini sudah ada!')
            return render(request, 'produk/create_produk.html', {'kategoriobj': Kategori.objects.all(), 'old_data': request.POST})

        # Validasi: minimal salah satu link harus diisi
        if not link_shopee and not link_tokopedia:
            messages.error(request, "Minimal isi salah satu link: Shopee atau Tokopedia.")
            return render(request, 'produk/create_produk.html', {'kategoriobj': Kategori.objects.all(), 'old_data': request.POST})

        # Ambil data kategori
        try:
            datakategori = Kategori.objects.get(id_kategori=idk)
        except (Kategori.DoesNotExist, ValueError):
            messages.error(request, "Kategori tidak ditemukan.")
            return render(request, 'produk/create_produk.html', {'kategoriobj': Kategori.objects.all(), 'old_data': request.POST})

        # Konversi thumbnail base64 ke file
        thumbnail_file = None
        if tb64 and "base64," in tb64:
            format, imgstr = tb64.split(';base64,')
            ext = format.split('/')[-1]
            thumbnail_file = ContentFile(base64.b64decode(imgstr), name=f"thumb_{np}.{ext}")

        # Simpan produk
        Produk.objects.create(
            id_kategori=datakategori,
            nama_produk=np,
            nomor_telepon=nt,
            deskripsi_produk=dp,
            gambar_produk=gp,
            thumbnail_produk=thumbnail_file,
            link_shopee=link_shopee,
            link_tokopedia=link_tokopedia,
            harga_produk=hp,
        )

        messages.success(request, 'Produk berhasil ditambahkan!')
        return redirect('read_produk')

def read_produk(request):
    produkobj = Produk.objects.all()
    if not produkobj.exists():
        messages.error(request, "Data produk tidak ditemukan!")
        return render(request, 'produk/read_produk.html', {'produkobj': None})
    else:
        return render(request, 'produk/read_produk.html', {'produkobj': produkobj})
    
@login_required(login_url="login")
@role_required(['admin']) 
def update_produk(request, id):
    getproduk = get_object_or_404(Produk, id_produk=id)
    kategoriobj = Kategori.objects.all()
    gambar_lama = getproduk.gambar_produk
    thumbnail_lama = getproduk.thumbnail_produk

    if request.method == 'GET':
        return render(request, 'produk/update_produk.html', {
            'getproduk': getproduk,
            'kategoriobj': kategoriobj
        })

    # POST
    idk = request.POST.get('id_kategori')
    np = request.POST.get('nama_produk')
    nt = request.POST.get('nomor_telepon')
    gp = request.FILES.get('gambar_produk')
    dp = request.POST.get('deskripsi_produk')
    ls = request.POST.get('link_shopee') or ''
    lt = request.POST.get('link_tokopedia') or ''
    hp = request.POST.get('harga_produk')
    tb64 = request.POST.get('thumbnail_base64')  # dari cropperjs

    # Validasi wajib diisi
    if not all([idk, np, nt, dp, ls, lt, hp]):
        messages.error(request, 'Semua field wajib diisi!')
        return render(request, 'produk/update_produk.html', {'getproduk': getproduk, 'kategoriobj': kategoriobj, 'old_data': request.POST})

    # Cek nama produk agar tidak duplikat
    if Produk.objects.filter(nama_produk=np).exclude(id_produk=id).exists():
        messages.error(request, 'Produk ini sudah ada!')
        return render(request, 'produk/update_produk.html', {'getproduk': getproduk, 'kategoriobj': kategoriobj, 'old_data': request.POST})

    # Update produk
    try:
        kategori_obj = Kategori.objects.get(id_kategori=idk)
    except (Kategori.DoesNotExist, ValueError):
        messages.error(request, 'Kategori tidak ditemukan.')
        return render(request, 'produk/update_produk.html', {'getproduk': getproduk, 'kategoriobj': kategoriobj, 'old_data': request.POST})

    getproduk.id_kategori = kategori_obj
    getproduk.nama_produk = np
    getproduk.nomor_telepon = nt
    getproduk.deskripsi_produk = dp
    getproduk.link_shopee = ls
    getproduk.link_tokopedia = lt
    getproduk.harga_produk = hp

    # Gambar Produk
    if gp:
        getproduk.gambar_produk = gp
    else:
        getproduk.gambar_produk = gambar_lama

    # Thumbnail (base64 string)
    if tb64:
        format, imgstr = tb64.split(';base64,')
        ext = format.split('/')[-1]  # jpg / png
        data = ContentFile(base64.b64decode(imgstr), name=f"thumb_{getproduk.id_produk}.{ext}")
        getproduk.thumbnail_produk = data
    else:
        getproduk.thumbnail_produk = thumbnail_lama

    getproduk.save()
    messages.success(request, 'Data produk berhasil diperbarui!')
    return redirect("read_produk")

    
def delete_produk(request, id):
    try:
        getproduk = Produk.objects.get(id_produk=id)  
        getproduk.delete()
        
        messages.success(request, "Data produk berhasil dihapus!")  
    except Produk.DoesNotExist:
        messages.error(request, "Produk tidak ditemukan.")
    
    return redirect('read_produk')

def read_detailproduk(request,id):
    try:
        getproduk = Produk.objects.get(id_produk=id)
        return render(request, 'produk/read_detailproduk.html', {'getproduk': getproduk})
    except Produk.DoesNotExist:
        messages.error(request, 'Produk tidak ditemukan.')
        return redirect('read_produk')

@login_required(login_url="login")
@role_required(['admin']) 
def create_bundling(request):
    produkobj = Produk.objects.all()
    if request.method == 'GET':
        return render(request, 'bundling/create_bundling.html', {'produkobj': produkobj})

    else:
        nb = request.POST.get('nama_bundling')
        gb = request.FILES.get('gambar_bundling')
        hb = request.POST.get('harga_bundling')
        lbt = request.POST.get('link_tokopedia')
        lbs = request.POST.get('link_shopee')
        db = request.POST.get('deskripsi_bundling')
        pd = request.POST.getlist('produk')
        tb64 = request.POST.get('thumbnail_base64')

        bundlings = Bundling.objects.filter(nama_bundling=nb)

        if bundlings.exists():
            messages.error(request, 'Nama bundling ini sudah ada!')
            return render(request, 'bundling/create_bundling.html', {'produkobj': produkobj, 'old_data': request.POST})

        if tb64 and "base64," in tb64:
            format, imgstr = tb64.split(';base64,')
            ext = format.split('/')[-1]
            thumbnail_file = ContentFile(base64.b64decode(imgstr), name=f"thumb_{nb}.{ext}")

        databundling = Bundling(
            nama_bundling= nb,
            gambar_bundling= gb,
            harga_bundling= int(hb),
            link_tokopedia= lbt,
            link_shopee= lbs,
            deskripsi_bundling= db,
            thumbnail_bundling = thumbnail_file
        )
        databundling.save()

        for produks in pd:
            try:
                prod = Produk.objects.get(id_produk = produks)
                DetailBundling(
                    id_bundling = databundling,
                    id_produk = prod,
                ).save()
            except (Produk.DoesNotExist, ValueError):
                continue

        messages.success(request, 'Data bundling berhasil ditambahkan!')
    return redirect("read_bundling")

def read_bundling(request):
    detailbundlingobj = DetailBundling.objects.all()
    bundlingobj = Bundling.objects.all()

    if not detailbundlingobj.exists():
        messages.error(request, 'Data Bundling Tidak Ditemukan!')
        return render(request,'bundling/read_bundling.html')
    
    else:
        return render(request, 'bundling/read_bundling.html', {
            'detailbundlingobj':detailbundlingobj,
            'bundlingobj':bundlingobj})


@login_required(login_url="login")
@role_required(['admin']) 
def update_bundling(request, id):
    bundling = get_object_or_404(Bundling, id_bundling=id)
    gambar_lama = bundling.gambar_bundling
    produkobj = Produk.objects.all()
    getdetailobj = DetailBundling.objects.filter(id_bundling=bundling)
    thumbnail_lama = bundling.thumbnail_bundling

    if request.method == "GET":
        return render(request, 'bundling/update_bundling.html', {
            'getdetailobj': getdetailobj,
            'produkobj': produkobj,
            'bundling': bundling
        })
    
    else:
        # Ambil data bundling dari POST
        nb = request.POST.get('nama_bundling')
        gb = request.FILES.get('gambar_bundling') 
        hb = request.POST.get('harga_bundling')
        lb = request.POST.get('link_bundling')
        db = request.POST.get('deskripsi_bundling')
        tb64 = request.POST.get('thumbnail_base64')  # dari cropperjs

        # Update bundling utama
        bundling.nama_bundling = nb
        bundling.harga_bundling = hb
        bundling.link_bundling = lb
        bundling.deskripsi_bundling = db
        bundling.gambar_bundling = gb if gb else gambar_lama

        # Thumbnail (base64 string)
        if tb64:
            format, imgstr = tb64.split(';base64,')
            ext = format.split('/')[-1]  # jpg / png
            data = ContentFile(base64.b64decode(imgstr), name=f"thumb_{bundling.id_bundling}.{ext}")
            bundling.thumbnail_bundling = data
        else:
            bundling.thumbnail_bundling = thumbnail_lama

        bundling.save()

        # Update detail produk
        produk_ids = request.POST.getlist('produk[]')
        DetailBundling.objects.filter(id_bundling=bundling).delete()  # hapus semua dulu

        for pid in produk_ids:
            produk = Produk.objects.get(id_produk=pid)
            DetailBundling.objects.create(id_bundling=bundling, id_produk=produk)

        messages.success(request, "Data bundling berhasil diperbarui!")
        return redirect('read_bundling')

@login_required(login_url="login")
@role_required(['admin']) 
def delete_bundling(request, id):
    try:
        getbundling = Bundling.objects.get(id_bundling=id)  
        getbundling.delete()
        
        messages.success(request, "Data bundling berhasil dihapus!")  
    except Bundling.DoesNotExist:
        messages.error(request, "Bundling tidak ditemukan.")
    
    return redirect('read_bundling')

def read_detailbundling(request, id):
    try:
        getbundling = Bundling.objects.get(id_bundling=id)
        getdetailbundling = DetailBundling.objects.filter(id_bundling = getbundling).select_related('id_produk')
        return render(request, 'bundling/read_detailbundling.html', {
            'getbundling': getbundling,
            'getdetailbundling': getdetailbundling})
    
    except Bundling.DoesNotExist:
        messages.error(request, 'Bundling tidak ditemukan.')
        return redirect('read_bundling')
