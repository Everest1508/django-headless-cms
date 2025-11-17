from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models, connection
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DetailView, FormView
from django.urls import reverse_lazy
from .models import Stack, DynamicTable, DynamicField, APIToken
from .serializers import StackSerializer, DynamicTableSerializer, DynamicFieldSerializer, DynamicDataSerializer, APITokenSerializer
from .dynamic_models import get_dynamic_model, create_dynamic_model


class DynamicTableViewSet(viewsets.ModelViewSet):
    """ViewSet for managing dynamic table definitions"""
    serializer_class = DynamicTableSerializer
    
    def get_queryset(self):
        """Return tables for the current user only"""
        queryset = DynamicTable.objects.filter(user=self.request.user)
        stack_id = self.request.query_params.get('stack')
        if stack_id:
            queryset = queryset.filter(stack_id=stack_id)
        return queryset
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a table"""
        serializer.save(user=self.request.user)
    
    def get_object(self):
        """Ensure user can only access their own tables"""
        obj = super().get_object()
        if obj.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this table.")
        return obj
    
    @action(detail=True, methods=['get', 'post', 'put', 'patch', 'delete'], url_path='data')
    def table_data(self, request, pk=None):
        """Handle CRUD operations for data in a dynamic table"""
        table = self.get_object()
        model_class = create_dynamic_model(table)
        
        # Check if table exists in database
        # Prepare the model first to ensure it's ready
        try:
            model_class._prepare()
        except:
            pass  # Model might already be prepared
        
        table_name = model_class._meta.db_table
        table_exists = False
        
        # Try to query the table directly (most reliable method)
        try:
            model_class.objects.all().count()
            table_exists = True
        except Exception as query_error:
            # If query fails, try a simple SQL check (avoiding Django's logging issues)
            try:
                # Use raw SQL without parameterized queries to avoid logging issues
                if connection.vendor == 'sqlite':
                    # Escape the table name and use direct string formatting
                    safe_table_name = table_name.replace("'", "''")
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{safe_table_name}'"
                        )
                        table_exists = cursor.fetchone() is not None
                elif connection.vendor == 'postgresql':
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT tablename FROM pg_tables WHERE tablename = %s",
                            (table_name,)
                        )
                        table_exists = cursor.fetchone() is not None
                elif connection.vendor == 'mysql':
                    with connection.cursor() as cursor:
                        safe_table_name = table_name.replace("'", "''")
                        cursor.execute(
                            f"SHOW TABLES LIKE '{safe_table_name}'"
                        )
                        table_exists = cursor.fetchone() is not None
                else:
                    table_exists = False
            except Exception:
                # If all checks fail, assume table doesn't exist
                table_exists = False
        
        if not table_exists:
            return Response({
                'error': f'Table "{table.name}" has not been created in the database yet.',
                'message': 'Please create the database table first by calling the migrate endpoint.',
                'migrate_endpoint': f'/api/tables/{table.id}/migrate/',
                'instructions': 'Send a POST request to the migrate endpoint to create the table.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'GET':
            # List all records or get single record by UUID
            try:
                record_id = request.query_params.get('id')
                if record_id:
                    # Get single record by UUID
                    import uuid
                    try:
                        uuid.UUID(str(record_id))
                        instance = model_class.objects.get(id=record_id)
                        serializer = DynamicDataSerializer(instance, model_class=model_class)
                        return Response(serializer.data)
                    except ValueError:
                        return Response({'error': 'Invalid UUID format'}, status=status.HTTP_400_BAD_REQUEST)
                    except model_class.DoesNotExist:
                        return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    # List all records
                    queryset = model_class.objects.all()
                    serializer = DynamicDataSerializer(queryset, many=True, model_class=model_class)
                    return Response(serializer.data)
            except Exception as e:
                return Response({
                    'error': f'Error querying table: {str(e)}',
                    'message': 'The table may not exist or there may be a schema mismatch.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif request.method == 'POST':
            # Create new record
            try:
                serializer = DynamicDataSerializer(data=request.data, model_class=model_class)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': f'Error creating record: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif request.method in ['PUT', 'PATCH']:
            # Update record - support both query parameter and request body
            record_id = request.query_params.get('id') or request.data.get('id')
            if not record_id:
                return Response({'error': 'ID (UUID) is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                import uuid
                # Validate UUID format
                uuid.UUID(str(record_id))
                instance = model_class.objects.get(id=record_id)
            except ValueError:
                return Response({'error': 'Invalid UUID format'}, status=status.HTTP_400_BAD_REQUEST)
            except model_class.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({
                    'error': f'Error querying record: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            try:
                serializer = DynamicDataSerializer(
                    instance, 
                    data=request.data, 
                    partial=request.method == 'PATCH',
                    model_class=model_class
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': f'Error updating record: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif request.method == 'DELETE':
            # Delete record
            record_id = request.query_params.get('id')
            if not record_id:
                return Response({'error': 'ID (UUID) is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                import uuid
                # Validate UUID format
                uuid.UUID(str(record_id))
                instance = model_class.objects.get(id=record_id)
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ValueError:
                return Response({'error': 'Invalid UUID format'}, status=status.HTTP_400_BAD_REQUEST)
            except model_class.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({
                    'error': f'Error deleting record: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='migrate')
    def migrate_table(self, request, pk=None):
        """Create database table for the dynamic model"""
        table = self.get_object()
        
        # Check if table has fields
        if not table.fields.exists():
            return Response({
                'error': f'Table "{table.name}" has no fields. Please add at least one field before creating the table.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        model_class = create_dynamic_model(table)
        table_name = model_class._meta.db_table
        
        # Prepare the model first
        try:
            model_class._prepare()
        except:
            pass  # Model might already be prepared
        
        # Check if table already exists
        table_exists = False
        try:
            model_class.objects.all().count()
            table_exists = True
        except Exception:
            # Check via SQL (using direct string to avoid logging issues)
            try:
                if connection.vendor == 'sqlite':
                    safe_table_name = table_name.replace("'", "''")
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{safe_table_name}'"
                        )
                        table_exists = cursor.fetchone() is not None
                elif connection.vendor == 'postgresql':
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT tablename FROM pg_tables WHERE tablename = %s",
                            (table_name,)
                        )
                        table_exists = cursor.fetchone() is not None
                elif connection.vendor == 'mysql':
                    safe_table_name = table_name.replace("'", "''")
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SHOW TABLES LIKE '{safe_table_name}'"
                        )
                        table_exists = cursor.fetchone() is not None
            except Exception:
                table_exists = False
        
        if table_exists:
            return Response({
                'message': f'Table {table.name} already exists',
                'api_endpoint': f'/api/tables/{table.id}/data/',
                'table_name': table_name
            }, status=status.HTTP_200_OK)
        
        try:
            # Prepare the model (this ensures all fields are properly set up)
            model_class._prepare()
            
            # Try to create the table in the database
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(model_class)
            
            # Verify table was created
            try:
                model_class.objects.all().count()
                table_created = True
            except Exception:
                table_created = False
            
            if not table_created:
                # Double check via SQL (using direct string to avoid logging issues)
                try:
                    if connection.vendor == 'sqlite':
                        safe_table_name = table_name.replace("'", "''")
                        with connection.cursor() as cursor:
                            cursor.execute(
                                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{safe_table_name}'"
                            )
                            table_created = cursor.fetchone() is not None
                    elif connection.vendor == 'postgresql':
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT tablename FROM pg_tables WHERE tablename = %s",
                                (table_name,)
                            )
                            table_created = cursor.fetchone() is not None
                    elif connection.vendor == 'mysql':
                        safe_table_name = table_name.replace("'", "''")
                        with connection.cursor() as cursor:
                            cursor.execute(
                                f"SHOW TABLES LIKE '{safe_table_name}'"
                            )
                            table_created = cursor.fetchone() is not None
                    else:
                        table_created = False
                except Exception:
                    table_created = False
            
            if table_created:
                return Response({
                    'message': f'Table {table.name} created successfully',
                    'api_endpoint': f'/api/tables/{table.id}/data/',
                    'table_name': table_name
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': f'Table creation appeared to succeed but table {table_name} was not found. Please check database logs.',
                    'table_name': table_name
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            # Check if error is because table already exists
            error_msg = str(e).lower()
            if 'already exists' in error_msg or 'duplicate' in error_msg or 'table already exists' in error_msg:
                return Response({
                    'message': f'Table {table.name} already exists',
                    'api_endpoint': f'/api/tables/{table.id}/data/',
                    'table_name': table_name
                }, status=status.HTTP_200_OK)
            return Response({
                'error': f'Failed to create table: {str(e)}',
                'table_name': table_name,
                'traceback': error_trace if settings.DEBUG else None
            }, status=status.HTTP_400_BAD_REQUEST)


class DynamicFieldViewSet(viewsets.ModelViewSet):
    """ViewSet for managing dynamic field definitions"""
    queryset = DynamicField.objects.all()
    serializer_class = DynamicFieldSerializer
    
    def get_queryset(self):
        queryset = DynamicField.objects.all()
        table_id = self.request.query_params.get('table')
        if table_id:
            queryset = queryset.filter(table_id=table_id)
        return queryset


class StackViewSet(viewsets.ModelViewSet):
    """ViewSet for managing stacks"""
    serializer_class = StackSerializer
    
    def get_queryset(self):
        """Return stacks for the current user only"""
        return Stack.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a stack"""
        serializer.save(user=self.request.user)
    
    def get_object(self):
        """Ensure user can only access their own stacks"""
        obj = super().get_object()
        if obj.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this stack.")
        return obj


# UI Views
class TableListView(LoginRequiredMixin, ListView):
    model = DynamicTable
    template_name = 'cms/table_list.html'
    context_object_name = 'tables'
    login_url = '/login/'
    
    def get_queryset(self):
        queryset = DynamicTable.objects.filter(user=self.request.user)
        stack_id = self.request.GET.get('stack')
        if stack_id:
            queryset = queryset.filter(stack_id=stack_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stacks'] = Stack.objects.filter(user=self.request.user).prefetch_related('content_types')
        stack_id = self.request.GET.get('stack')
        if stack_id:
            try:
                context['current_stack'] = Stack.objects.get(id=stack_id, user=self.request.user)
            except Stack.DoesNotExist:
                pass
        return context


class TableCreateView(LoginRequiredMixin, CreateView):
    model = DynamicTable
    template_name = 'cms/table_form.html'
    fields = ['name', 'display_name', 'description']
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_types'] = DynamicField.FIELD_TYPES
        stack_id = self.request.GET.get('stack')
        if stack_id:
            try:
                context['stack'] = Stack.objects.get(id=stack_id, user=self.request.user)
            except Stack.DoesNotExist:
                pass
        context['stacks'] = Stack.objects.filter(user=self.request.user)
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        stack_id = self.request.GET.get('stack') or self.request.POST.get('stack')
        if stack_id:
            try:
                stack = Stack.objects.get(id=stack_id, user=self.request.user)
                form.instance.stack = stack
            except Stack.DoesNotExist:
                pass
        response = super().form_valid(form)
        # Handle fields from form data
        # The form is submitted via JavaScript/API, so this might not be called
        # But we keep it for fallback
        return response
    
    def get_success_url(self):
        return reverse_lazy('table_detail', kwargs={'pk': self.object.id})


class TableUpdateView(LoginRequiredMixin, UpdateView):
    model = DynamicTable
    template_name = 'cms/table_form.html'
    fields = ['name', 'display_name', 'description']
    login_url = '/login/'
    
    def get_queryset(self):
        """Only allow users to edit their own tables"""
        return DynamicTable.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_types'] = DynamicField.FIELD_TYPES
        fields_queryset = self.object.fields.all()
        # Serialize fields to JSON for JavaScript
        import json
        fields_data = []
        for field in fields_queryset:
            fields_data.append({
                'id': field.id,
                'name': field.name,
                'display_name': field.display_name,
                'field_type': field.field_type,
                'required': field.required,
                'max_length': field.max_length,
                'default_value': field.default_value or '',
                'help_text': field.help_text or '',
                'order': field.order
            })
        context['fields'] = fields_queryset  # Keep for template loops if needed
        context['fields_json'] = json.dumps(fields_data)  # JSON for JavaScript
        context['stacks'] = Stack.objects.filter(user=self.request.user)
        context['is_edit'] = True
        return context
    
    def form_valid(self, form):
        stack_id = self.request.POST.get('stack')
        if stack_id:
            try:
                stack = Stack.objects.get(id=stack_id, user=self.request.user)
                form.instance.stack = stack
            except Stack.DoesNotExist:
                pass
        elif stack_id == '':
            form.instance.stack = None
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('table_detail', kwargs={'pk': self.object.id})


class TableDetailView(LoginRequiredMixin, DetailView):
    model = DynamicTable
    template_name = 'cms/table_detail.html'
    context_object_name = 'table'
    login_url = '/login/'
    
    def get_queryset(self):
        """Only allow users to view their own tables"""
        return DynamicTable.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = self.object.fields.all()
        
        # Check if table exists in database
        from .dynamic_models import create_dynamic_model
        model_class = create_dynamic_model(self.object)
        table_name = model_class._meta.db_table
        table_exists = False
        
        try:
            # First try to query the table directly (most reliable)
            try:
                model_class.objects.all().count()
                table_exists = True
            except Exception:
                # If query fails, check via SQL
                with connection.cursor() as cursor:
                    if connection.vendor == 'sqlite':
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                            (table_name,)
                        )
                        table_exists = cursor.fetchone() is not None
                    elif connection.vendor == 'postgresql':
                        cursor.execute(
                            "SELECT tablename FROM pg_tables WHERE tablename = %s",
                            (table_name,)
                        )
                        table_exists = cursor.fetchone() is not None
                    elif connection.vendor == 'mysql':
                        cursor.execute(
                            "SHOW TABLES LIKE %s",
                            (table_name,)
                        )
                        table_exists = cursor.fetchone() is not None
                    else:
                        table_exists = False
        except Exception:
            table_exists = False
        
        context['table_exists'] = table_exists
        return context


def home_view(request):
    """Home page with table management UI"""
    if request.user.is_authenticated:
        tables = DynamicTable.objects.filter(user=request.user)
    else:
        tables = DynamicTable.objects.none()
    return render(request, 'cms/home.html', {'tables': tables, 'user': request.user})


class RegisterView(FormView):
    """User registration view"""
    template_name = 'cms/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


def logout_view(request):
    """Logout view"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')


@login_required
def api_explorer_view(request):
    """API Explorer page"""
    tables = DynamicTable.objects.filter(user=request.user)
    return render(request, 'cms/api_explorer.html', {
        'tables': tables,
        'base_url': request.build_absolute_uri('/')[:-1]  # Remove trailing slash
    })


class APITokenViewSet(viewsets.ModelViewSet):
    """ViewSet for managing API tokens"""
    serializer_class = APITokenSerializer
    
    def get_queryset(self):
        """Return tokens for the current user only"""
        return APIToken.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a token"""
        serializer.save(user=self.request.user)


@login_required
def api_tokens_view(request):
    """API Tokens management page"""
    tokens = APIToken.objects.filter(user=request.user)
    return render(request, 'cms/api_tokens.html', {
        'tokens': tokens,
        'base_url': request.build_absolute_uri('/')[:-1]
    })


# Stack UI Views
class StackListView(LoginRequiredMixin, ListView):
    model = Stack
    template_name = 'cms/stack_list.html'
    context_object_name = 'stacks'
    login_url = '/login/'
    
    def get_queryset(self):
        return Stack.objects.filter(user=self.request.user).prefetch_related('content_types')


class StackCreateView(LoginRequiredMixin, CreateView):
    model = Stack
    template_name = 'cms/stack_form.html'
    fields = ['name', 'display_name', 'description']
    success_url = reverse_lazy('stack_list')
    login_url = '/login/'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class StackUpdateView(LoginRequiredMixin, UpdateView):
    model = Stack
    template_name = 'cms/stack_form.html'
    fields = ['name', 'display_name', 'description']
    success_url = reverse_lazy('stack_list')
    login_url = '/login/'
    
    def get_queryset(self):
        """Only allow users to edit their own stacks"""
        return Stack.objects.filter(user=self.request.user)


class StackDetailView(LoginRequiredMixin, DetailView):
    model = Stack
    template_name = 'cms/stack_detail.html'
    context_object_name = 'stack'
    login_url = '/login/'
    
    def get_queryset(self):
        """Only allow users to view their own stacks"""
        return Stack.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_types'] = self.object.content_types.all()
        return context
