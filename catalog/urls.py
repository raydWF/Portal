from django.urls import path
from . import views
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from django.conf.urls import include

urlpatterns = [
	
	path('', views.index, name='index'),
	
	path('construction/', views.construction, name='under_construction'),



]

urlpatterns += [

	path('keys/', views.KeyListView.as_view(), name='keys'),

	path('key/<int:pk>/detail', views.KeyDetailView.as_view(), name='roomkey-detail'),

	path('key/<int:pk>/request', views.KeyRequestCreate.as_view(), name='roomkey-request'),

	path('mykeys/', views.LoanedKeysByUserListView.as_view(), name='borrowed-keys'),

	path('key/<uuid:pk>/renew/', views.renew_key_user, name='renew-key-user'),

	path('borrowedKeys/', views.LoanedKeysAllListView.as_view(), name='all-borrowed-keys'),

	path('key/agreement', views.KeyAgreement, name='key-agreement'),

	path('keys/all-requests', views.KeyRequestListView.as_view(), name='all-requested-keys'),

	path('keys/request/<int:pk>', views.KeyRequestDetailView.as_view(), name='key-request-detail'),

	path('keys/request/<int:pk>/update', views.KeyRequestUpdate.as_view(), name='key-request-update'),

]

urlpatterns += [

	path('maintenance/', views.MaintenanceListView.as_view(), name='maintenance-home'),

	path('maintenance-wip/', views.MaintenanceRequestListView.as_view(), name='wip-maintenance'),

	path('maintenance/<int:pk>', views.MaintenanceRequestDetailView.as_view(), name='maintenancerequest-detail'),

	path('maintenance-completed/', views.CompletedMaintenanceListView.as_view(), name='completed-maintenance'),

	path('maintenance/create/', views.MaintenanceRequestCreate.as_view(), name='maintenance_create'),

	path('maintenance/<int:pk>/update/', views.MaintenanceRequestUpdate.as_view(), name='maintenancerequest_update'),

]

urlpatterns += [

	path('move-request/', views.MoveRequestListView.as_view(), name='move-home'),


]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]