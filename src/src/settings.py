"""
Django settings for src project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)

PROJECT_NAME = "Mineral Inventory Agent" # This will change the project name across several parts of the project
PROJECT_URL = "https://example.com" # This will change the project URL across several parts of the project

### CHANGE THE CODE BELOW TO MANAGE WHICH APPS TO USE ###
## djast.dev is intended to be used with all the apps below, but you can personalize it at your own risk ##
apps = [
    ('allauth.socialaccount.providers.google', False), # Google OAuth Social Login
    ('allauth.socialaccount.providers.github', False), # Github OAuth Social Login
    ('admin_interface', True), # Custom Admin Interface
    ('rest_framework', True), # REST API Framework
    ('drf_spectacular', True), # API Documentation
    ('axes', True), # Security package
    ('api', True), # Public API Endpoints
    ('agents', True), # Document Store Agent
    ('supervisor', True), # Super Admin Panel
    ('error_handling', True), # Error Handling
    ('legal', True), # Legal Pages
    ('chat', True), # Chat Interface
    ('tailwind', True), # Tailwind CSS
    ('django_browser_reload', False), # Automatically reloads the browser when you save a file
    ('django_elasticsearch_dsl', True), # Elasticsearch DSL
    ('cognito_jwt', not DEBUG), # AWS Cognito JWT Authentication
]

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = config('SECRET_KEY', default='YOUR_SECRET_KEY')

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0', '.vercel.app']

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
            
INTERNAL_IPS = [
    "127.0.0.1",
]


ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'context_processors.project_name',
                'context_processors.google_analytics_id',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
} if DEBUG else {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='postgres'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default='6543'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# AWS Cognito Configuration
AWS_COGNITO_REGION = config('AWS_COGNITO_REGION', default='us-east-1')
AWS_COGNITO_USER_POOL_ID = config('AWS_COGNITO_USER_POOL_ID', default='')
AWS_COGNITO_APP_CLIENT_ID = config('AWS_COGNITO_APP_CLIENT_ID', default='')
AWS_COGNITO_APP_CLIENT_SECRET = config('AWS_COGNITO_APP_CLIENT_SECRET', default='')
AWS_COGNITO_DOMAIN = config('AWS_COGNITO_DOMAIN', default='')

# Function to define Cognito authentication settings
def define_cognito_settings():
    global REST_FRAMEWORK, COGNITO_JWT_SETTINGS
    
    # Configure REST framework for JWT authentication
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'cognito_jwt.django_auth.JSONWebTokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema' if 'drf_spectacular' in INSTALLED_APPS else None
    }
    
    # Configure Cognito JWT settings
    COGNITO_JWT_SETTINGS = {
        'AWS_REGION': AWS_COGNITO_REGION,
        'USER_POOL_ID': AWS_COGNITO_USER_POOL_ID,
        'APP_CLIENT_ID': AWS_COGNITO_APP_CLIENT_ID,
        'TOKEN_LOCATION': 'HEADER',
        'TOKEN_HEADER_NAME': 'Authorization',
    }

### These settings are used to enable or disable certain features in the project dynamically based on 'apps' variable ###
## You don't need to change anything here (unless you want to), just add or remove apps from the 'apps' variable above ##
# CHANGE THE CODE BELOW AT YOUR OWN RISK #
def define_django_allauth_settings(social_providers = []):
    ''' Django Allauth Settings '''
    global AUTHENTICATION_BACKENDS, SOCIALACCOUNT_PROVIDERS, ACCOUNT_AUTHENTICATION_METHOD, ACCOUNT_EMAIL_REQUIRED, ACCOUNT_USERNAME_REQUIRED, ACCOUNT_EMAIL_VERIFICATION, EMAIL_BACKEND, DEFAULT_FROM_EMAIL
    
    if len(social_providers) > 0:
        SOCIALACCOUNT_PROVIDERS = {}
        for social_provider in social_providers:
            if social_provider == 'google':
                SOCIALACCOUNT_PROVIDERS['google'] = {
                    'APP': {
                        'client_id': config('GOOGLE_CLIENT_ID', default=''),
                        'secret': config('GOOGLE_SECRET', default=''),
                        'key': ''
                    },
                    'SCOPE': [
                        'profile',
                        'email',
                    ],
                    'AUTH_PARAMS': {
                        'access_type': 'offline',
                    },
                    'OAUTH_PKCE_ENABLED': True,
                }
            elif social_provider == 'github':
                SOCIALACCOUNT_PROVIDERS['github'] = {
                    'APP': {
                        'client_id': config('GITHUB_CLIENT_ID', default=''),
                        'secret': config('GITHUB_SECRET', default=''),
                        'key': ''
                    },
                    'SCOPE': [
                        'user:email', 
                    ],
                }
    else:
        # Modify authentication backends based on environment
        AUTHENTICATION_BACKENDS = []
        
        if ('axes', True) in apps:
            AUTHENTICATION_BACKENDS = [
                'axes.backends.AxesStandaloneBackend',
            ]
            
        AUTHENTICATION_BACKENDS += [
            'django.contrib.auth.backends.ModelBackend',
        ]
        
        # Add django-allauth backend only when in DEBUG mode or when social providers are configured
        if DEBUG or len(social_providers) > 0:
            if 'allauth' in INSTALLED_APPS:
                AUTHENTICATION_BACKENDS += [
                    'allauth.account.auth_backends.AuthenticationBackend'
                ]
        
        # Make both username and email required
        ACCOUNT_USERNAME_REQUIRED = config('ACCOUNT_USERNAME_REQUIRED', default=True, cast=bool)
        ACCOUNT_EMAIL_REQUIRED = config('ACCOUNT_EMAIL_REQUIRED', default=True, cast=bool)

        # Allow login via either username or email
        ACCOUNT_AUTHENTICATION_METHOD = config('ACCOUNT_AUTHENTICATION_METHOD', default='username_email')

        # Send a verification email, but don't require it for login
        ACCOUNT_EMAIL_VERIFICATION = config('ACCOUNT_EMAIL_VERIFICATION', default='mandatory')

        if DEBUG:
            EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        else:
            EMAIL_BACKEND = None
        DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')

def define_django_axes_settings():
    ''' Django Axes Settings '''
    global AXES_FAILURE_LIMIT, AXES_COOLOFF_TIME, AXES_RESET_ON_SUCCESS
    
    AXES_FAILURE_LIMIT = config('AXES_FAILURE_LIMIT', default=10, cast=int)    
    AXES_COOLOFF_TIME = config('AXES_COOLOFF_TIME', default=1, cast=int)
    AXES_RESET_ON_SUCCESS = config('AXES_RESET_ON_SUCCESS', default=True, cast=bool)

AUTHENTICATION_REQUIRED = config('AUTHENTICATION_REQUIRED', default=True, cast=bool)      
if AUTHENTICATION_REQUIRED:
    INSTALLED_APPS.append('django.contrib.sites')
    INSTALLED_APPS.append('user_management.apps.UserManagementConfig')
    INSTALLED_APPS.append('allauth')
    INSTALLED_APPS.append('allauth.account')
    define_django_allauth_settings()

GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default=None)

social_providers = []
for app, should_add in apps:
    if should_add and app not in INSTALLED_APPS:
        if 'allauth.socialaccount.' in app and 'allauth.socialaccount' not in INSTALLED_APPS:
            if not AUTHENTICATION_REQUIRED:
                raise Exception('Social accounts require authentication to be enabled. Enable AUTHENTICATION_REQUIRED in your .env file.')
            INSTALLED_APPS.append('allauth.socialaccount')
        INSTALLED_APPS.append(app)
        if 'allauth.socialaccount.providers.' in app:
            social_providers.append(app.replace('allauth.socialaccount.providers.', ''))
        if app == 'tailwind':
            INSTALLED_APPS.append('theme')
            TAILWIND_APP_NAME = 'theme'
        elif app == 'admin_interface':
            INSTALLED_APPS.append('colorfield')
            INSTALLED_APPS = ['admin_interface', 'colorfield'] + [i for i in INSTALLED_APPS if i not in ['admin_interface', 'colorfield']]
            X_FRAME_OPTIONS = "SAMEORIGIN"
            SILENCED_SYSTEM_CHECKS = ["security.W019"]
        elif app == 'axes':
            define_django_axes_settings()
INSTALLED_APPS.append('shared')

if len(social_providers) > 0:
    define_django_allauth_settings(social_providers)

if 'user_management.apps.UserManagementConfig' in INSTALLED_APPS:
    MIDDLEWARE.append('user_management.middleware.LoginRequiredMiddleware')
if 'django_browser_reload' in INSTALLED_APPS:
    MIDDLEWARE.append('django_browser_reload.middleware.BrowserReloadMiddleware')
if 'allauth' in INSTALLED_APPS:
    MIDDLEWARE.append('allauth.account.middleware.AccountMiddleware')
if 'axes' in INSTALLED_APPS:
    MIDDLEWARE.append('axes.middleware.AxesMiddleware')

# Apply Cognito settings in production
if not DEBUG and 'cognito_jwt' in INSTALLED_APPS:
    define_cognito_settings()

import warnings

if 'YOUR_SECRET_KEY' in SECRET_KEY:
    warnings.warn('Please set a secure SECRET_KEY in your .env file.', UserWarning)

# ChromaDB configuration (read from the .env file)
CHROMADB_PERSIST_DIRECTORY = config('CHROMADB_PERSIST_DIRECTORY', default=os.path.join(BASE_DIR, 'chromadb_persist'))
CHROMADB_API_HOST = config('CHROMADB_API_HOST', default='localhost')
CHROMADB_API_PORT = config('CHROMADB_API_PORT', default='8000')

ENCRYPTION_KEY = config('ENCRYPTION_KEY', default='YOUR_ENCRYTION_KEY')
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': config('ELASTICSEARCH_HOST', default='localhost:9200')
    },
}
#### END OF CUSTOM CONFIGURATION SETTINGS ####

# Modify REST framework settings to include JWT authentication in production
if 'rest_framework' in INSTALLED_APPS and 'drf_spectacular' in INSTALLED_APPS:
    if not DEBUG and 'cognito_jwt' in INSTALLED_APPS:
        # Already configured in define_cognito_settings
        pass
    else:
        REST_FRAMEWORK = {
            'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
        }

    SPECTACULAR_SETTINGS = {
        'TITLE': f'{PROJECT_NAME} API',
        'DESCRIPTION': 'API documentation for all endpoints',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': False,
        'SECURITY': [{'Bearer': []} if not DEBUG and 'cognito_jwt' in INSTALLED_APPS else {},]
    }