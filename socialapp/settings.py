from pathlib import Path
import os
import dj_database_url  # Required for production database settings
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Load environment variables from .env file
load_dotenv()  # This loads environment variables from the .env file

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Cloudinary Configuration
cloudinary.config( 
  cloud_name = os.getenv("CLOUD_NAME"), 
  api_key = os.getenv("API_KEY"), 
  api_secret = os.getenv("API_SECRET")
)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv("CLOUD_NAME"),
    'API_KEY': os.getenv("API_KEY"),
    'API_SECRET': os.getenv("API_SECRET"),
}

# SECURITY WARNING: Keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-default-secret-key")

# SECURITY WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ["true", "1"]

# Set allowed hosts for production and local development
ALLOWED_HOSTS = ['ivallap.onrender.com', '127.0.0.1', 'localhost']

# CSRF Trusted Origins (add your deployed domain)
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'https://ivallap.onrender.com'
]

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',  # For handling static files in production
    'users',
    'posts',
    'channels',
    'cloudinary',
    'cloudinary_storage',
]

# Custom user model
AUTH_USER_MODEL = "users.CustomUser"

# Email settings (Use environment variables for security)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "karrilokesh108@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "ionu rkyl ckqd dtyr")  # ⚠️ Use environment variable

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",  # For serving static files
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URLs
ROOT_URLCONF = 'socialapp.urls'

# Session Settings
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Includes app templates automatically
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'posts.context_processors.notification_count',
                'django.contrib.messages.context_processors.messages',
                'posts.context_processors.unread_messages_count',
                'posts.context_processors.get_recent_stories',  # Custom context processor
            ],
        },
    },
]

# WSGI Application
WSGI_APPLICATION = 'socialapp.wsgi.application'

# ASGI Configuration for Channels
ASGI_APPLICATION = 'socialapp.asgi.application'

# Channel Layers for real-time features
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Database (Uses SQLite for local development, PostgreSQL for production)

DATABASES = {
    'default': dj_database_url.parse(
        'postgresql://ivallapp_ezs1_user:gpG6HK6j0qwNZtGZR04L7ei7XeiriwgZ@dpg-d23qj3vdiees739ujm4g-a.oregon-postgres.render.com:5432/ivallapp_ezs1',
        conn_max_age=600,
        ssl_require=True
    )
}

# DATABASES = {
#     'default': dj_database_url.config(
#         default='postgresql://loki:GmV7z0zmg8NvAMLPj8bTM5GHLVlXENw9@dpg-d05kbbqli9vc738svja0-a.oregon-postgres.render.com/loki_236q',
#         conn_max_age=600
#     )
# }
# Use PostgreSQL on Render (Ensure your DATABASE_URL is set correctly)
if not DEBUG:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=False)

# Password validation settings
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static & Media files
STATIC_URL = "/static/"

# STATIC_ROOT will store the collected static files during production
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Authentication URLs
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

