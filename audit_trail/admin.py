from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from .models import AuditTrail
from .watcher import AuditTrailWatcher


class ContentTypeFilter(SimpleListFilter):
    title = _('content type')
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        result = []
        for model in AuditTrailWatcher.tracked_models:
            content_type = ContentType.objects.get_for_model(model)
            result.append((content_type.id, content_type.name))
        return result

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=self.value())
        else:
            return queryset


def action(audit_trail):
    colors = {
        AuditTrail.ACTIONS.DELETED: '#FF7575',
        AuditTrail.ACTIONS.CREATED: '#27DE55',
        AuditTrail.ACTIONS.UPDATED: '#FFFF84',
    }
    row_template = u'<div style="background-color: %s; padding: 5px; border-radius: 3px; font-weight: bold">%s</div>'

    if audit_trail.action in [AuditTrail.ACTIONS.CREATED, AuditTrail.ACTIONS.UPDATED, AuditTrail.ACTIONS.DELETED]:

        return row_template % (colors[audit_trail.action], audit_trail.get_action_display())
    if audit_trail.is_related_changed:
        return row_template % (
            colors[audit_trail.related_trail.action],
            u'Related ' + audit_trail.related_trail.get_action_display().lower()
        )

action.short_description = _('Action')
action.allow_tags = True


def render_changes(audit_trail):
    changes = audit_trail.get_changes()
    return render_to_string('audit_trail/changes.html', {'audit_trail': audit_trail, 'changes': changes})

render_changes.short_description = _('Changes')
render_changes.allow_tags = True


class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('id', 'action_time', 'content_type', action, 'user', 'user_ip', 'object_repr', render_changes)
    list_display_links = None
    list_filter = (ContentTypeFilter, 'action',)
    search_fields = ('object_id', )
    actions = None

    def __init__(self, *args, **kwargs):
        super(AuditTrailAdmin, self).__init__(*args, **kwargs)

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return False
        return True

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
