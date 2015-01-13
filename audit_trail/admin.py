from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.template.loader import render_to_string

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


def action(audit_trail):
    color = ''

    if audit_trail.is_deleted:
        color = '#FF7575'

    if audit_trail.is_created:
        color = '#27DE55'

    if audit_trail.is_updated:
        color = '#FFFF84'

    return u'<div style="background-color: %s; padding: 5px; border-radius: 3px; font-weight: bold">%s</div>' % (
        color, audit_trail.get_action_display()
    )

action.allow_tags = True


def render_changes(audit_trail):
    changes = audit_trail.get_changes()
    return render_to_string('audit_trail/changes.html', {'audit_trail': audit_trail, 'changes': changes})

render_changes.allow_tags = True


class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('action_time', action, 'user', 'user_ip', 'content_type', 'object_repr', render_changes)
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
        return obj.get_formatted_changes()

    format_json_values.short_description = 'Changes'
    format_json_values.allow_tags = True
    

admin.site.register(AuditTrail, AuditTrailAdmin)
