"""
Django Headless CMS - A powerful headless CMS built with Django REST Framework
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read version from __init__.py
version = {}
with open('cms/__init__.py', 'r') as f:
    exec(f.read(), version)

setup(
    name='django-headless-cms',
    version=version.get('__version__', '0.1.0'),
    description='A powerful headless CMS built with Django REST Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/django-headless-cms',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*', 'core', 'core.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django>=4.2,<6.0',
        'djangorestframework>=3.14.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django cms headless rest api content management',
    project_urls={
        'Documentation': 'https://github.com/yourusername/django-headless-cms#readme',
        'Source': 'https://github.com/yourusername/django-headless-cms',
        'Tracker': 'https://github.com/yourusername/django-headless-cms/issues',
    },
)

