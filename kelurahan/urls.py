from django.urls import path
from . import views

urlpatterns = [

    path('login', views.loginview, name='login'),
    path('performlogin', views.performlogin, name='performlogin'),
    path('performlogout', views.performlogout, name='performlogout'),
    path('', views.base, name='base'),
     
# # CRUD kategori
    path('create_kategori', views.create_kategori, name='create_kategori'),   
    path('read_kategori', views.read_kategori,name='read_kategori'),
    path('update_kategori/<str:id>/', views.update_kategori,name='update_kategori'),
    path('delete_kategori/<str:id>/', views.delete_kategori,name='delete_kategori'),

# # CRUD produk
    path('create_produk', views.create_produk, name='create_produk'),
    path('read_produk', views.read_produk,name='read_produk'),
    path('update_produk/<int:id>/', views.update_produk,name='update_produk'),
    path('read_detailproduk/<int:id>/', views.read_detailproduk,name='read_detailproduk'),
    path('delete_produk/<str:id>/', views.delete_produk,name='delete_produk'),
# # CRUD kegiatan
    path('create_kegiatan', views.create_kegiatan, name='create_kegiatan'),
    path('read_kegiatan', views.read_kegiatan,name='read_kegiatan'),
    path('update_kegiatan/<int:id>/', views.update_kegiatan,name='update_kegiatan'),
    path('read_detailkegiatan/<int:id>/', views.read_detailkegiatan,name='read_detailkegiatan'),
    path('delete_kegiatan/<str:id>/', views.delete_kegiatan,name='delete_kegiatan'),
# # CRUD bundling
    path('create_bundling', views.create_bundling, name='create_bundling'),
    path('read_bundling', views.read_bundling,name='read_bundling'),
    path('read_detailbundling/<str:id>/', views.read_detailbundling,name='read_detailbundling'),
    path('update_bundling/<str:id>/', views.update_bundling,name='update_bundling'),
    path('delete_bundling/<str:id>/', views.delete_bundling,name='delete_bundling'),
]