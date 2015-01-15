# Audit Trail library

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
