# Installation Guide

## Install as a Package

### From GitHub (Recommended)

Install directly from GitHub repository:

```bash
# Install from main/master branch
pip install git+https://github.com/yourusername/django-headless-cms.git

# Install from a specific branch
pip install git+https://github.com/yourusername/django-headless-cms.git@develop

# Install from a specific tag/version
pip install git+https://github.com/yourusername/django-headless-cms.git@v0.1.0

# Install with SSH (if you have access)
pip install git+ssh://git@github.com/yourusername/django-headless-cms.git
```

**Note**: Replace `yourusername` with your actual GitHub username.

### From PyPI (when published)

```bash
pip install django-headless-cms
```

### From Local Source

```bash
# Clone the repository
git clone https://github.com/yourusername/django-headless-cms.git
cd django-headless-cms

# Install in development mode (editable)
pip install -e .

# Or install normally
pip install .
```

### From Local Directory

If you have the package locally:

```bash
pip install /path/to/django-headless-cms
```

## Django Project Setup

### 1. Add to INSTALLED_APPS

In your Django project's `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    
    # Your apps
    'cms',  # Add Django Headless CMS
]
```

### 2. Configure REST Framework

Add to your `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'cms.authentication.APITokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CSRF settings for API compatibility
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000'] if DEBUG else []
```

### 3. Configure Static and Media Files

Add to your `settings.py`:

```python
# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 4. Add URLs

In your main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cms.urls')),  # Add CMS URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Server

```bash
python manage.py runserver
```

## Verify Installation

1. Visit http://127.0.0.1:8000/ - You should see the CMS home page
2. Visit http://127.0.0.1:8000/api/ - You should see the API browser
3. Register/Login to start using the CMS

## Troubleshooting

### Templates Not Found

If templates are not loading, make sure:
- The package is properly installed
- `cms` is in `INSTALLED_APPS`
- You've run `python manage.py collectstatic` (for production)

### Static Files Not Loading

Run:
```bash
python manage.py collectstatic
```

### Migration Errors

If you encounter migration errors:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Development Installation

For development, install with editable mode:

```bash
pip install -e .
```

This allows you to make changes to the package without reinstalling.

