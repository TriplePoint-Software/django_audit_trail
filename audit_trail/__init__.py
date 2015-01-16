from watcher import AuditTrailWatcher


def audit_trail_watch(cls, **kwargs):
    related_watcher = AuditTrailWatcher(**kwargs)
    if related_watcher.contribute_to_class(cls):
        related_watcher.init_signals()

default_app_config = 'audit_trail.app.AuditTrailAppConfig'