from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import export_mayors_permit, import_mayors_permit
from rest_framework.routers import DefaultRouter
from .api import TricycleViewSet


router = DefaultRouter()
router.register(r'api/tricycles', TricycleViewSet)

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
    path('mayors-permit-tri/datatable/', views.mayors_permit_tricycle_datatable, name='mayors-permit-tri-datatable'),
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
    path('franchise/add/', views.add_franchise, name='add-franchise'),
    path('franchise/update/', views.update_franchise, name='update-franchise'),
    # path('api/admin/<int:admin_id>/', views.get_admin_details, name='get_admin_details'),
    path('export-idcards/', views.export_idcards_with_images, name='export-idcards'),
    path('import-idcards/', views.import_idcards_with_images, name='import-idcards'),
    path('mtop/import/', views.import_mtop, name='import-mtop'),
    path('mtop/export/', views.export_mtop, name='export-mtop'),
    path('mtop/datatable/', views.mtop_datatable, name='mtop-datatable'),
    path('franchise/import/', views.import_franchise, name='import-franchise'),
    path('franchise/export/', views.export_franchise, name='export-franchise'),
    path('mayors-permit/datatable/', views.mayors_permit_datatable, name='mayors-permit-datatable'),
    path('mayors-permit/history-data/<int:permit_id>/', views.get_permit_history, name='get-permit-history'),
    path('mayors-permit-tri/history-data/<int:permit_id>/', 
         views.mayors_permit_tri_history_data, 
         name='mayors-permit-tri-history-data'),
    
    path('create-report-tri/', views.create_report_tri, name='create-report-tri'),
    path('create-report-tri-datatable/', views.create_report_tri_datatable, name='create-report-tri-datatable'),
    path('export-create-report-tri/', views.export_create_report_tri, name='export-create-report-tri'),
    path('import-create-report-tri/', views.import_create_report_tri, name='import-create-report-tri'),
    path('add-tricycle/', views.add_tricycle, name='add-tricycle'),
    path('update-tricycle/', views.update_tricycle, name='update-tricycle'),  # Add this line
    path('franchise/datatable/', views.franchise_datatable, name='franchise-datatable'),
    path('id-cards/datatable/', views.id_cards_datatable, name='id-cards-datatable'),

    path('tricycles/list/', views.get_tricycles, name='get-tricycles'),
    path('', include(router.urls))

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

