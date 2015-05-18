# myapp/signals/signals.py
from django.dispatch import Signal

# pylint: disable=C0103
audit_trail_app_ready = Signal()
