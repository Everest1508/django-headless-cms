from rest_framework import serializers
from django.db import models
from .models import Stack, DynamicTable, DynamicField, APIToken


class StackSerializer(serializers.ModelSerializer):
    """Serializer for Stack model"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    content_types_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Stack
        fields = ['id', 'user', 'name', 'display_name', 'description', 
                  'created_at', 'updated_at', 'content_types_count']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'content_types_count']
    
    def get_content_types_count(self, obj):
        """Return the number of content types in this stack"""
        return obj.content_types.count()


class DynamicFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicField
        fields = ['id', 'name', 'display_name', 'field_type', 'required', 
                  'max_length', 'default_value', 'help_text', 'order']
        read_only_fields = ['id']


class DynamicTableSerializer(serializers.ModelSerializer):
    fields = DynamicFieldSerializer(many=True, required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    stack = serializers.PrimaryKeyRelatedField(
        queryset=Stack.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = DynamicTable
        fields = ['id', 'user', 'stack', 'name', 'display_name', 'description', 
                  'created_at', 'updated_at', 'fields']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        table = DynamicTable.objects.create(**validated_data)
        
        for field_data in fields_data:
            DynamicField.objects.create(table=table, **field_data)
        
        return table
    
    def update(self, instance, validated_data):
        fields_data = validated_data.pop('fields', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if fields_data is not None:
            # Delete existing fields not in the update
            existing_field_ids = [f['id'] for f in fields_data if 'id' in f]
            instance.fields.exclude(id__in=existing_field_ids).delete()
            
            # Update or create fields
            for field_data in fields_data:
                field_id = field_data.pop('id', None)
                if field_id:
                    DynamicField.objects.filter(id=field_id, table=instance).update(**field_data)
                else:
                    DynamicField.objects.create(table=instance, **field_data)
        
        return instance


class DynamicDataSerializer(serializers.Serializer):
    """Generic serializer for dynamic table data"""
    def __init__(self, *args, **kwargs):
        self.model_class = kwargs.pop('model_class', None)
        super().__init__(*args, **kwargs)
        
        if self.model_class:
            # Dynamically add fields based on the model
            for field in self.model_class._meta.get_fields():
                if not field.many_to_many and not field.one_to_many:
                    # Handle primary key (UUID) field
                    if field.primary_key:
                        self.fields['id'] = serializers.UUIDField(read_only=True)
                        continue
                    
                    field_kwargs = {'required': not field.null and not field.blank}
                    
                    # Determine serializer field type based on Django field type
                    field_class = field.__class__.__name__
                    
                    if field_class == 'CharField':
                        serializer_field = serializers.CharField
                        if hasattr(field, 'max_length'):
                            field_kwargs['max_length'] = field.max_length
                    elif field_class == 'TextField':
                        serializer_field = serializers.CharField
                    elif field_class == 'IntegerField':
                        serializer_field = serializers.IntegerField
                    elif field_class == 'FloatField':
                        serializer_field = serializers.FloatField
                    elif field_class == 'BooleanField':
                        serializer_field = serializers.BooleanField
                    elif field_class == 'DateField':
                        serializer_field = serializers.DateField
                    elif field_class == 'DateTimeField':
                        serializer_field = serializers.DateTimeField
                    elif field_class == 'EmailField':
                        serializer_field = serializers.EmailField
                        if hasattr(field, 'max_length'):
                            field_kwargs['max_length'] = field.max_length
                    elif field_class == 'URLField':
                        serializer_field = serializers.URLField
                        if hasattr(field, 'max_length'):
                            field_kwargs['max_length'] = field.max_length
                    elif field_class == 'UUIDField':
                        serializer_field = serializers.UUIDField
                    elif field_class in ['ImageField', 'FileField']:
                        serializer_field = serializers.FileField
                        field_kwargs['required'] = False  # Files can be optional
                    else:
                        serializer_field = serializers.CharField
                    
                    # Add default value if exists
                    if hasattr(field, 'default') and field.default != models.NOT_PROVIDED:
                        if not callable(field.default):
                            field_kwargs['default'] = field.default
                    
                    self.fields[field.name] = serializer_field(**field_kwargs)
    
    def create(self, validated_data):
        if not self.model_class:
            raise serializers.ValidationError("Model class not provided")
        return self.model_class.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        if not self.model_class:
            raise serializers.ValidationError("Model class not provided")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class APITokenSerializer(serializers.ModelSerializer):
    """Serializer for API tokens"""
    key = serializers.CharField(read_only=True)
    last_used = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = APIToken
        fields = ['id', 'name', 'key', 'created_at', 'last_used', 'is_active']
        read_only_fields = ['id', 'key', 'created_at', 'last_used']

