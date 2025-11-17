# Installing from GitHub

Yes! You can install this package directly from GitHub using pip.

## Quick Install

```bash
pip install git+https://github.com/yourusername/django-headless-cms.git
```

Replace `yourusername` with your actual GitHub username.

## Installation Options

### Install from Main Branch

```bash
pip install git+https://github.com/yourusername/django-headless-cms.git
```

### Install from Specific Branch

```bash
pip install git+https://github.com/yourusername/django-headless-cms.git@develop
```

### Install from Specific Tag/Version

```bash
pip install git+https://github.com/yourusername/django-headless-cms.git@v0.1.0
```

### Install with SSH (if you have access)

```bash
pip install git+ssh://git@github.com/yourusername/django-headless-cms.git
```

### Install in Editable Mode (for development)

```bash
# Clone first
git clone https://github.com/yourusername/django-headless-cms.git
cd django-headless-cms

# Install in editable mode
pip install -e .
```

## Requirements

- Git must be installed on your system
- pip version 19.0 or higher (supports VCS installs)

## After Installation

1. Add `'cms'` to `INSTALLED_APPS` in your Django settings
2. Configure REST Framework settings
3. Run migrations: `python manage.py migrate`
4. Start using the CMS!

See `INSTALLATION.md` for complete setup instructions.

## Updating

To update to the latest version from GitHub:

```bash
pip install --upgrade git+https://github.com/yourusername/django-headless-cms.git
```

## Troubleshooting

### Git not found

If you get an error about git not being found:
- Install Git: https://git-scm.com/downloads
- Make sure Git is in your PATH

### Permission errors

If you get permission errors:
- Use `pip install --user` for user installation
- Or use a virtual environment (recommended)

### SSL errors

If you encounter SSL errors:
- Use `git+https://` instead of `git://`
- Or configure Git SSL settings

