from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from .models import AuditTrail
from .watcher import AuditTrailWatcher


class ContentTypeFilter(SimpleListFilter):
    title = 'content type'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        result = []
        for model in AuditTrailWatcher.tracked_models:
            ct = ContentType.objects.get_for_model(model)
            result.append((ct.id, ct.name))
        return result

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=self.value())
        else:
            return queryset
       

class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'user_ip', 'content_type', 'object_repr', 'format_json_values')
    list_filter = (ContentTypeFilter, 'action')
    actions = None

    def __init__(self, *args, **kwargs):
        super(AuditTrailAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)

    def has_add_permission(self, request):
        return False

    def has_save_permission(self, *args):
        return False

    def has_delete_permission(self, *args):
        return False

    def format_json_values(self, obj):
        return obj.get_formatted_values()

    format_json_values.short_description = 'Changes'
    format_json_values.allow_tags = True
    

admin.site.register(AuditTrail, AuditTrailAdmin)
