# Packaging Guide

This guide explains how to package and distribute Django Headless CMS.

## Building the Package

### Prerequisites

```bash
pip install setuptools wheel twine
```

### Build Distribution

```bash
# Build source distribution and wheel
python setup.py sdist bdist_wheel

# Or using build (recommended)
python -m build
```

This will create:
- `dist/django-headless-cms-0.1.0.tar.gz` (source distribution)
- `dist/django-headless-cms-0.1.0-py3-none-any.whl` (wheel)

## Testing the Package

### Test Installation

```bash
# Install from local build
pip install dist/django-headless-cms-0.1.0-py3-none-any.whl

# Or from source distribution
pip install dist/django-headless-cms-0.1.0.tar.gz
```

### Test in a New Virtual Environment

```bash
# Create new virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the package
pip install dist/django-headless-cms-0.1.0-py3-none-any.whl

# Test import
python -c "import cms; print(cms.__version__)"
```

## Publishing to PyPI

### Test PyPI (for testing)

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ django-headless-cms
```

### Production PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install django-headless-cms
```

## Version Management

Update version in:
1. `cms/__init__.py` - `__version__ = '0.1.0'`
2. `setup.py` - reads from `cms/__init__.py`
3. `pyproject.toml` - `version = "0.1.0"`

## Package Structure

```
django-headless-cms/
├── cms/                    # Main package
│   ├── __init__.py        # Version info
│   ├── apps.py            # App config
│   ├── models.py          # Models
│   ├── views.py           # Views
│   ├── serializers.py     # Serializers
│   ├── urls.py            # URLs
│   ├── authentication.py  # Auth
│   ├── dynamic_models.py  # Dynamic models
│   ├── templatetags/      # Template tags
│   └── migrations/        # Migrations
├── templates/             # Templates (included via MANIFEST.in)
├── setup.py               # Setup script
├── setup.cfg              # Setup config
├── pyproject.toml         # Modern Python packaging
├── MANIFEST.in            # Files to include
├── README.md              # Documentation
├── LICENSE                # License
└── requirements.txt       # Dependencies
```

## Using Makefile

```bash
# Install in development mode
make install-dev

# Build package
make build

# Clean build artifacts
make clean

# Check package
make check
```

## Checklist Before Publishing

- [ ] Update version number in all files
- [ ] Update CHANGELOG.md (if exists)
- [ ] Test installation in clean environment
- [ ] Verify all files are included (templates, static, etc.)
- [ ] Test with different Python versions
- [ ] Test with different Django versions
- [ ] Update README with latest features
- [ ] Tag release in git: `git tag v0.1.0`

