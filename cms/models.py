from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class Stack(models.Model):
    """Model to group content types together"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stacks'
    )
    name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
                message='Stack name must start with a letter and contain only letters, numbers, and underscores.'
            )
        ]
    )
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user', 'name']]  # Stack name must be unique per user
        ordering = ['-created_at']
        verbose_name = 'Stack'
        verbose_name_plural = 'Stacks'
    
    def __str__(self):
        return self.display_name or self.name


class DynamicTable(models.Model):
    """Model to store table definitions"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dynamic_tables',
        null=True,  # Allow null temporarily for migration
        blank=True
    )
    stack = models.ForeignKey(
        Stack,
        on_delete=models.CASCADE,
        related_name='content_types',
        null=True,  # Allow null for backward compatibility
        blank=True
    )
    name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
                message='Table name must start with a letter and contain only letters, numbers, and underscores.'
            )
        ]
    )
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['stack', 'name']]  # Table name must be unique per stack
        ordering = ['-created_at']
        verbose_name = 'Dynamic Table'
        verbose_name_plural = 'Dynamic Tables'
    
    def __str__(self):
        return self.display_name or self.name


class DynamicField(models.Model):
    """Model to store field definitions for dynamic tables"""
    
    FIELD_TYPES = [
        ('CharField', 'Text'),
        ('TextField', 'Long Text'),
        ('IntegerField', 'Integer'),
        ('FloatField', 'Decimal'),
        ('BooleanField', 'Boolean'),
        ('DateField', 'Date'),
        ('DateTimeField', 'Date & Time'),
        ('EmailField', 'Email'),
        ('URLField', 'URL'),
        ('ImageField', 'Image'),
        ('FileField', 'File'),
    ]
    
    table = models.ForeignKey(
        DynamicTable,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
                message='Field name must start with a letter and contain only letters, numbers, and underscores.'
            )
        ]
    )
    display_name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    max_length = models.IntegerField(null=True, blank=True, help_text='For CharField only')
    default_value = models.CharField(max_length=500, blank=True, null=True)
    help_text = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = [['table', 'name']]
        verbose_name = 'Dynamic Field'
        verbose_name_plural = 'Dynamic Fields'
    
    def __str__(self):
        return f"{self.table.name}.{self.name}"


class APIToken(models.Model):
    """Model to store API tokens for users"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_tokens'
    )
    name = models.CharField(
        max_length=100,
        help_text='A descriptive name for this token (e.g., "Production API", "Development")'
    )
    key = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API Token'
        verbose_name_plural = 'API Tokens'
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.key:
            import secrets
            self.key = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
