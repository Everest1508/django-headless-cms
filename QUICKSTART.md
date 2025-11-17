# Quick Start Guide

## Installation

### From GitHub

```bash
pip install git+https://github.com/yourusername/django-headless-cms.git
```

### From PyPI (when published)

```bash
pip install django-headless-cms
```

**Note**: Replace `yourusername` with your actual GitHub username.

## Setup

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'cms',
]
```

### 2. Configure REST Framework

```python
# settings.py
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
```

### 3. Add URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ... your URLs
    path('', include('cms.urls')),
]
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ and start creating content types!

