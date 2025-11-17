"""
Dynamic model generation system for creating Django models at runtime
"""
import uuid
from django.db import models
from django.apps import apps
from django.core.exceptions import ValidationError
from .models import DynamicTable, DynamicField


def get_django_field(field_def):
    """Convert DynamicField to Django model field"""
    field_type = field_def.field_type
    kwargs = {}
    
    if field_def.help_text:
        kwargs['help_text'] = field_def.help_text
    
    if field_type == 'CharField':
        kwargs['max_length'] = field_def.max_length or 255
        if field_def.default_value:
            kwargs['default'] = field_def.default_value
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        return models.CharField(**kwargs)
    
    elif field_type == 'TextField':
        if field_def.default_value:
            kwargs['default'] = field_def.default_value
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        return models.TextField(**kwargs)
    
    elif field_type == 'IntegerField':
        if field_def.default_value:
            try:
                kwargs['default'] = int(field_def.default_value)
            except ValueError:
                pass
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        return models.IntegerField(**kwargs)
    
    elif field_type == 'FloatField':
        if field_def.default_value:
            try:
                kwargs['default'] = float(field_def.default_value)
            except ValueError:
                pass
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        return models.FloatField(**kwargs)
    
    elif field_type == 'BooleanField':
        if field_def.default_value:
            kwargs['default'] = field_def.default_value.lower() in ('true', '1', 'yes')
        else:
            kwargs['default'] = False
        return models.BooleanField(**kwargs)
    
    elif field_type == 'DateField':
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        return models.DateField(**kwargs)
    
    elif field_type == 'DateTimeField':
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        return models.DateTimeField(**kwargs)
    
    elif field_type == 'EmailField':
        kwargs['max_length'] = field_def.max_length or 254
        if field_def.default_value:
            kwargs['default'] = field_def.default_value
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        return models.EmailField(**kwargs)
    
    elif field_type == 'URLField':
        kwargs['max_length'] = field_def.max_length or 200
        if field_def.default_value:
            kwargs['default'] = field_def.default_value
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        return models.URLField(**kwargs)
    
    elif field_type == 'ImageField':
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        # Use a simple string path, not a callable
        kwargs['upload_to'] = 'dynamic_uploads/'
        return models.ImageField(**kwargs)
    
    elif field_type == 'FileField':
        if not field_def.required:
            kwargs['blank'] = True
            kwargs['null'] = True
        # Use a simple string path, not a callable
        kwargs['upload_to'] = 'dynamic_uploads/'
        return models.FileField(**kwargs)
    
    else:
        raise ValueError(f"Unknown field type: {field_type}")


def create_dynamic_model(table_def):
    """Create a Django model class dynamically from DynamicTable definition"""
    fields = {}
    meta_attrs = {
        'app_label': 'cms',
        'verbose_name': table_def.display_name,
        'verbose_name_plural': table_def.display_name,
        'db_table': f'cms_{table_def.name.lower()}',
    }
    
    # Add UUID primary key field
    fields['id'] = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for this record'
    )
    
    # Add all fields from DynamicField
    for field_def in table_def.fields.all():
        fields[field_def.name] = get_django_field(field_def)
    
    # Create the model class
    model_name = table_def.name
    model_class = type(
        model_name,
        (models.Model,),
        {
            '__module__': 'cms.dynamic_models',
            'Meta': type('Meta', (), meta_attrs),
            **fields
        }
    )
    
    return model_class


def get_dynamic_model(table_name):
    """Get a dynamically created model by table name"""
    try:
        table_def = DynamicTable.objects.get(name=table_name)
        return create_dynamic_model(table_def)
    except DynamicTable.DoesNotExist:
        return None


def register_dynamic_models():
    """Register all dynamic models with Django's app registry"""
    # This is called after migrations to ensure all tables are available
    for table_def in DynamicTable.objects.all():
        model_class = create_dynamic_model(table_def)
        # Register with app registry
        app_config = apps.get_app_config('cms')
        app_config.models[table_def.name.lower()] = model_class

