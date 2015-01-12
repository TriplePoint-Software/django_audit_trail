__author__ = 'syabro'


class AuditTrailFormatter(object):
    @classmethod
    def format(cls, action_flag, data):
        from .models import AuditTrail
        method = 'format_' + {
            AuditTrail.ACTIONS.CREATED: 'created',
            AuditTrail.ACTIONS.UPDATED: 'updated',
            AuditTrail.ACTIONS.DELETED: 'deleted'
        }[action_flag]
        return getattr(cls, method)(data)

    @classmethod
    def format_created(cls, data):
        result = []
        for item in data:
            result.append('<b>"%s"</b>=<b>"%s"</b>' % (item[0], item[2]))
        return 'created with %s' % (', '.join(result))

    @classmethod
    def format_updated(cls, data):
        result = []
        for item in data:
            result.append('<b>"%s"</b> changed from <b>"%s"</b> to <b>"%s"</b>' % tuple(item))
        return '<br />'.join(result)

    @classmethod
    def format_deleted(cls, data):
        result = []
        for item in data:
            result.append('<b>"%s"</b>=<b>"%s"</b>' % (item[0], item[2]))
        return 'deleted where %s' % (', '.join(result))