from django.contrib import admin
from .models import DynamicTable, DynamicField


class DynamicFieldInline(admin.TabularInline):
    model = DynamicField
    extra = 1
    fields = ('name', 'display_name', 'field_type', 'required', 'max_length', 'order')


@admin.register(DynamicTable)
class DynamicTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'display_name')
    inlines = [DynamicFieldInline]


@admin.register(DynamicField)
class DynamicFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'table', 'field_type', 'required', 'order')
    list_filter = ('field_type', 'required', 'table')
    search_fields = ('name', 'table__name')
