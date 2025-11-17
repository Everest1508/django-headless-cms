from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import (
    DynamicTableViewSet, 
    DynamicFieldViewSet,
    StackViewSet,
    APITokenViewSet,
    home_view,
    TableListView,
    TableCreateView,
    TableUpdateView,
    TableDetailView,
    StackListView,
    StackCreateView,
    StackUpdateView,
    StackDetailView,
    RegisterView,
    logout_view,
    api_explorer_view,
    api_tokens_view
)

router = DefaultRouter()
router.register(r'tables', DynamicTableViewSet, basename='table')
router.register(r'fields', DynamicFieldViewSet, basename='field')
router.register(r'stacks', StackViewSet, basename='stack')
router.register(r'tokens', APITokenViewSet, basename='token')

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='cms/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('stacks/', StackListView.as_view(), name='stack_list'),
    path('stacks/create/', StackCreateView.as_view(), name='stack_create'),
    path('stacks/<int:pk>/', StackDetailView.as_view(), name='stack_detail'),
    path('stacks/<int:pk>/edit/', StackUpdateView.as_view(), name='stack_edit'),
    path('tables/', TableListView.as_view(), name='table_list'),
    path('tables/create/', TableCreateView.as_view(), name='table_create'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='table_detail'),
    path('tables/<int:pk>/edit/', TableUpdateView.as_view(), name='table_edit'),
    path('api-explorer/', api_explorer_view, name='api_explorer'),
    path('api-tokens/', api_tokens_view, name='api_tokens'),
    path('api/', include(router.urls)),
]

