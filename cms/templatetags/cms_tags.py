from django import template
import json

register = template.Library()


@register.filter
def example_json(table, request_type='post'):
    """
    Generate example JSON for a table based on its fields.
    request_type can be 'post' or 'put'
    """
    fields = table.fields.all()
    example_data = {}
    
    if request_type == 'put':
        example_data['id'] = '550e8400-e29b-41d4-a716-446655440000'  # Example UUID
    
    for field in fields:
        # Skip id field for POST (it's auto-generated)
        if field.name == 'id':
            continue
            
        field_type = field.field_type
        field_name = field.name
        
        # Generate example value based on field type
        if field_type in ['CharField', 'TextField']:
            example_data[field_name] = f"example_{field_name}"
        elif field_type == 'IntegerField':
            example_data[field_name] = 42
        elif field_type == 'FloatField':
            example_data[field_name] = 99.99
        elif field_type == 'BooleanField':
            example_data[field_name] = True
        elif field_type == 'DateField':
            example_data[field_name] = "2024-01-15"
        elif field_type == 'DateTimeField':
            example_data[field_name] = "2024-01-15T10:30:00Z"
        elif field_type == 'EmailField':
            example_data[field_name] = f"example@{field_name}.com"
        elif field_type == 'URLField':
            example_data[field_name] = f"https://example.com/{field_name}"
        elif field_type in ['ImageField', 'FileField']:
            # For file fields, we'll show a placeholder
            example_data[field_name] = None  # Files are uploaded differently
        else:
            example_data[field_name] = f"example_{field_name}"
    
    # Remove None values (like file fields)
    example_data = {k: v for k, v in example_data.items() if v is not None}
    
    return json.dumps(example_data, indent=2)


@register.filter
def example_json_curl(table, request_type='post'):
    """
    Generate example JSON for cURL command (single line, escaped)
    """
    fields = table.fields.all()
    example_data = {}
    
    if request_type == 'put':
        example_data['id'] = '550e8400-e29b-41d4-a716-446655440000'  # Example UUID
    
    for field in fields:
        if field.name == 'id':
            continue
            
        field_type = field.field_type
        field_name = field.name
        
        if field_type in ['CharField', 'TextField']:
            example_data[field_name] = f"example_{field_name}"
        elif field_type == 'IntegerField':
            example_data[field_name] = 42
        elif field_type == 'FloatField':
            example_data[field_name] = 99.99
        elif field_type == 'BooleanField':
            example_data[field_name] = True
        elif field_type == 'DateField':
            example_data[field_name] = "2024-01-15"
        elif field_type == 'DateTimeField':
            example_data[field_name] = "2024-01-15T10:30:00Z"
        elif field_type == 'EmailField':
            example_data[field_name] = f"example@{field_name}.com"
        elif field_type == 'URLField':
            example_data[field_name] = f"https://example.com/{field_name}"
        elif field_type in ['ImageField', 'FileField']:
            continue  # Skip file fields in cURL examples
        else:
            example_data[field_name] = f"example_{field_name}"
    
    return json.dumps(example_data)


