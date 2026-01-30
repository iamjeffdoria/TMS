from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import export_mayors_permit, import_mayors_permit

urlpatterns = [
    path('', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admins/add/', views.add_admin, name='add_admin'),
    path('admins/update/', views.update_admin, name='update_admin'),

    path('admin-list/', views.admin_list, name='admin-list'),
    path('mayors-permit/', views.mayors_permit, name='mayors-permit'),
    path('add-mayors-permit/', views.add_mayors_permit, name='add-mayors-permit'),
    path('id-cards/', views.id_cards, name='id-cards'),
    path('mayors-permit/update/<int:permit_id>/', views.update_mayors_permit, name='update-mayors-permit'),
    path('permit-renewal/', views.permit_renewal, name='permit-renewal'),
    path("mayors-permit/print/<int:pk>/", views.print_mayors_permit, name="print-mayors-permit"),
    path("mtop", views.mtop, name="mtop"),
    path('mtop/<int:pk>/print/', views.mtop_print, name='mtop_print'),
    path('franchise/', views.franchise, name='franchise'),
    path('mayors-permit-tricycle/', views.mayors_permit_tricycle, name='mayors-permit-tricycle'),
    path('export-mayors-permit/', export_mayors_permit, name='export-mayors-permit'),
    path('export-mayors-permit-tri/', views.export_mayors_permit_tri, name='export-mayors-permit-tri'),
    path('import-mayors-permit-tri/', views.import_mayors_permit_tri, name='import-mayors-permit-tri'),
    path('import-mayors-permit/', import_mayors_permit, name='import-mayors-permit'),
    path('sample-print/', views.sample_print, name='sample-print'),
    path('api/permits/<str:control_no>/', views.permit_detail_api),
    path("add-idcard/", views.add_idcard, name="add-idcard"),
    path('add-mayors-permit-tri/', views.add_permit_tri, name='add-mayors-permit-tri'),
    path('mayors-permit-history/', views.mayors_permit_history, name='mayors-permit-history'),
    path('update-permit/<int:permit_id>/', views.update_permit_tri, name='update_permit'),
    path('admin-management/', views.admin_management, name='admin-management'),
    path('update-idcard/', views.update_idcard, name='update-idcard'),
    path("mtop/add/", views.add_mtop, name="add-mtop"),
    path("mtop/get/<int:id>/", views.get_mtop, name="get_mtop"),
    path("mtop/update/", views.update_mtop, name="update_mtop"),
    # urls.py
    path(
    'mayors-permit/<int:permit_id>/history/',
    views.mayors_permit_history,
    name='mayors-permit-history'
    ),
    path('mayors-permit-tri-history/<int:permit_id>/', views.mayors_permit_tri_history, name='mayors-permit-tri-history'),
    path('franchise/add/', views.add_franchise, name='add-franchise'),
    path('franchise/update/', views.update_franchise, name='update-franchise'),
    # path('api/admin/<int:admin_id>/', views.get_admin_details, name='get_admin_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

