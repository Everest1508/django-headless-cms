# Django Headless CMS

A powerful headless CMS built with Django REST Framework that allows you to create database tables dynamically through a user-friendly UI, with automatic API generation.

## Features

- 🎨 **Modern UI**: Beautiful, responsive interface for creating and managing tables
- 🚀 **Dynamic Table Creation**: Create database tables from the UI without writing code
- 📡 **Auto-generated APIs**: RESTful APIs are automatically created for each table
- 🔧 **Flexible Field Types**: Support for various field types (Text, Integer, Date, Image, File, etc.)
- 📊 **Table Management**: View, edit, and manage all your dynamic tables
- 🎯 **REST Framework Integration**: Full Django REST Framework support with browsable API
- 🗂️ **Stack Management**: Organize content types into stacks
- 🔑 **API Token Authentication**: Secure API access with token-based authentication
- ✏️ **Edit Content Types**: Edit existing content types and their fields

## Installation

### Install from GitHub

You can install directly from GitHub:

```bash
# Install from main branch
pip install git+https://github.com/yourusername/django-headless-cms.git

# Install from a specific branch
pip install git+https://github.com/yourusername/django-headless-cms.git@develop

# Install from a specific tag/version
pip install git+https://github.com/yourusername/django-headless-cms.git@v0.1.0
```

### Install from PyPI (when published)

```bash
pip install django-headless-cms
```

### Install from Local Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/django-headless-cms.git
   cd django-headless-cms
   ```

2. **Install the package**:
   ```bash
   # Install in editable/development mode
   pip install -e .

   # Or install normally
   pip install .
   ```

### Setup in Your Django Project

1. **Add to INSTALLED_APPS** in your `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ... other apps
       'rest_framework',
       'cms',  # Add this
   ]
   ```

2. **Configure REST Framework** (add to `settings.py`):
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
   ```

3. **Configure Static and Media Files** (add to `settings.py`):
   ```python
   STATIC_URL = '/static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   STATICFILES_DIRS = [
       BASE_DIR / 'static',
   ]

   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   ```

4. **Add URLs** to your main `urls.py`:
   ```python
   from django.urls import path, include
   from django.conf import settings
   from django.conf.urls.static import static

   urlpatterns = [
       # ... your other URLs
       path('', include('cms.urls')),
   ]

   # Serve media files in development
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Home/UI: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API Browser: http://127.0.0.1:8000/api/

## Quick Start

After installation, you can start using the CMS immediately:

1. **Login/Register**: Create an account or login at http://127.0.0.1:8000/
2. **Create a Stack**: Organize your content types into stacks
3. **Create Content Types**: Define your content structure
4. **Create Database Tables**: Migrate your content types to create actual database tables
5. **Use the API**: Access your data via RESTful APIs

## Usage

### Creating a Stack

1. Navigate to "Stacks" in the sidebar
2. Click "Create Stack"
3. Fill in stack details:
   - **Display Name**: A friendly name (e.g., "My Blog")
   - **API Name**: A unique identifier (e.g., `my_blog`)
   - **Description**: Optional description

### Creating a Content Type

1. Navigate to the home page at http://127.0.0.1:8000/
2. Click "Create New Table"
3. Fill in the table details:
   - **Table Name**: A unique identifier (e.g., `products`, `blog_posts`)
   - **Display Name**: A human-readable name (e.g., "Products", "Blog Posts")
   - **Description**: Optional description
4. Add fields to your table:
   - Click "+ Add Field" to add a new field
   - Configure each field:
     - Field Name (e.g., `title`, `price`)
     - Display Name (e.g., "Title", "Price")
     - Field Type (Text, Integer, Date, Image, etc.)
     - Required/Optional
     - Max Length (for text fields)
     - Default Value (optional)
     - Help Text (optional)
5. Click "Create Content Type"

### Creating the Database Table

After creating a content type definition:

1. Go to the content type detail page
2. Click "Create Database Table" button
3. This will create the actual database table with UUID primary keys

### Using the API

Once a table is created and migrated, you can use the REST API:

#### List all records
```bash
GET /api/tables/{table_id}/data/
```

#### Create a new record
```bash
POST /api/tables/{table_id}/data/
Content-Type: application/json

{
  "field1": "value1",
  "field2": "value2"
}
```

#### Get a single record by UUID
```bash
GET /api/tables/{table_id}/data/?id={uuid}
```

#### Update a record
```bash
PUT /api/tables/{table_id}/data/?id={uuid}
Content-Type: application/json

{
  "field1": "updated_value1",
  "field2": "updated_value2"
}
```

#### Delete a record
```bash
DELETE /api/tables/{table_id}/data/?id={uuid}
```

**Note**: All records use UUID as primary keys instead of integer IDs for better security.

### API Endpoints

- **List all content types**: `GET /api/tables/`
- **Create content type**: `POST /api/tables/`
- **Content type details**: `GET /api/tables/{id}/`
- **List records**: `GET /api/tables/{id}/data/`
- **Get single record**: `GET /api/tables/{id}/data/?id={uuid}`
- **Create record**: `POST /api/tables/{id}/data/`
- **Update record**: `PUT /api/tables/{id}/data/?id={uuid}`
- **Delete record**: `DELETE /api/tables/{id}/data/?id={uuid}`
- **Migrate table**: `POST /api/tables/{id}/migrate/`
- **List stacks**: `GET /api/stacks/`
- **Create stack**: `POST /api/stacks/`
- **List API tokens**: `GET /api/tokens/`
- **Create API token**: `POST /api/tokens/`

## Project Structure

```
django-headless-cms/
├── core/                 # Main project settings
│   ├── settings.py      # Django settings (includes media/static config)
│   └── urls.py          # Main URL configuration
├── cms/                  # CMS application
│   ├── models.py        # DynamicTable and DynamicField models
│   ├── views.py         # API viewsets and UI views
│   ├── serializers.py   # DRF serializers
│   ├── dynamic_models.py # Dynamic model generation
│   ├── urls.py          # CMS URL routing
│   └── admin.py         # Admin configuration
├── templates/           # HTML templates
│   └── cms/            # CMS templates
├── static/              # Static files (CSS, JS, images)
├── media/               # User-uploaded media files
└── manage.py           # Django management script
```

## Configuration

### Media and Static Files

The project is configured with:

- **Static URL**: `/static/`
- **Static Root**: `staticfiles/` (for production)
- **Static Files Dirs**: `static/` (for development)
- **Media URL**: `/media/`
- **Media Root**: `media/`

These settings are already configured in `core/settings.py`.

### REST Framework Settings

Default REST Framework configuration:
- Permissions: AllowAny (change for production)
- Pagination: 20 items per page

## Field Types Supported

- **CharField**: Text (with max length)
- **TextField**: Long text
- **IntegerField**: Whole numbers
- **FloatField**: Decimal numbers
- **BooleanField**: True/False
- **DateField**: Date only
- **DateTimeField**: Date and time
- **EmailField**: Email addresses
- **URLField**: URLs
- **ImageField**: Image uploads
- **FileField**: File uploads

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Production Considerations

1. **Security**: Change `DEBUG = False` and set `ALLOWED_HOSTS`
2. **Permissions**: Update REST Framework permissions for production
3. **Static Files**: Run `python manage.py collectstatic`
4. **Database**: Use PostgreSQL or MySQL instead of SQLite
5. **Media Storage**: Consider using cloud storage (S3, etc.) for media files
6. **CSRF**: Ensure CSRF protection is properly configured

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

