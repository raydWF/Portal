from django.contrib import admin
from .models import *

# Register your models here.
class KeyInstanceInline(admin.TabularInline):
	model = KeyInstance	

@admin.register(RoomKey)
class RoomKeyAdmin(admin.ModelAdmin):
	list_display = ('room_name', 'room_des', 'key_symb', 'bitting_num', 'office')
	inlines = [KeyInstanceInline]

@admin.register(KeyInstance)
class KeyInstanceAdmin(admin.ModelAdmin):
	list_display = ('roomkey', 'keyrequest', 'status', 'date_out', 'borrower','due_back', 'key_notes', 'id')

	list_filter = ('roomkey', 'status','due_back')

@admin.register(KeyRequest)
class KeyRequest(admin.ModelAdmin):
	list_display = ('roomkey', 'request_status', 'requester','borrower', 'date_requested', 'date_completed','request_comments')

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
	list_display = ('requester', 'office', 'urgency', 'status', 'date_submitted', 'date_completed', 'request_comments')

@admin.register(MoveRequest)
class MoveRequestAdmin(admin.ModelAdmin):
	list_display = ('move_person', 'move_to', 'move_date', 'move_conditions', 'requested_by')

# ====================================================================================================
