# Audit Trail library

### Syabro: Unfinished. Fix after implementing in the main project

Model history tracking

## Usage

```python
    class MyModel(models.Model):
        field1, field2, field3 = models.IntegerField(), models.IntegerField(), models.IntegerField()
        field4, field5         = models.TextField(), models.TextField()
        
        audit = AuditTrailWatcher(
            fields=['field1', 'field2'],
            track_creation=True,
            track_update=True,
            track_deletion=True,
            track_related=['somemodel_set', 'somefk']
        )
```

## Options

**fields** — list of fields to track. If is not provided — track all fields.  
**track_creation** — track model creation, default True  
**track_update** — track model update, default True  
**track_deletion** — track model deletion, default True  
**track_related** - track related objects changes

[![Code Health](https://landscape.io/github/TriplePoint-Software/django_audit_trail/master/landscape.svg?style=flat)](https://landscape.io/github/TriplePoint-Software/django_audit_trail/master)

[![Code Issues](http://www.quantifiedcode.com/api/v1/project/88c190ebca044e088164a8d95255f85c/badge.svg)](http://www.quantifiedcode.com/app/project/88c190ebca044e088164a8d95255f85c)
