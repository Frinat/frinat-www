# -*- coding: UTF-8 -*-
import os

from configurations import Configuration, values

gettext = lambda s: s

DJANGO_BASE = os.path.dirname(os.path.dirname(__file__))
PROJECT_BASE = os.path.dirname(DJANGO_BASE)


class DebugFlags(Configuration):
    DEBUG = values.BooleanValue(True)

    @property
    def MEDIA_DEBUG(self):
        return self.DEBUG

    @property
    def STATICFILES_DEBUG(self):
        return self.DEBUG

    @property
    def TEMPLATE_DEBUG(self):
        return self.DEBUG


class CMSConfig(object):
    CMS_PAGE_MEDIA_PATH = 'assets/cms/'
    CMS_TEMPLATES = (
        ('left-sidebar.html', gettext('Left sidebar')),
        ('full.html', gettext('Full width (no sidebar)')),
        ('index.html', gettext('Homepage template')),
    )
    CMS_PLACEHOLDER_CONF = {
        'content': {
            'plugins': (
                'TextPlugin', 'PicturePlugin', 'FilePlugin', 'SnippetPlugin',
                'LinkPlugin', 'MapPlugin', 'CMSCalendarMonthPlugin',
                'CMSLatestEntriesPlugin', 'CMSSelectedEntriesPlugin',
                'CMSSelectedPeoplePlugin', 'CMSPeopleGroupPlugin'
            ),
        },
        'sidebar': {
            'plugins': ('CMSRandomSponsorPlugin', 'CMSSpecificSponsorPlugin'),
        },
    }
    CMS_MENU_TITLE_OVERWRITE = True
    CMS_PERMISSION = True
    CMS_SEO_FIELDS = True
    CMS_SOFTROOT = False
    CMS_LANGUAGES = {
        1: [
            {
                'code': 'fr',
                'name': gettext('French'),
            }
        ],
        'default': {
            'fallbacks': ['fr'],
            'redirect_on_fallback': True,
            'public': True,
            'hide_untranslated': False,
        }
    }
    #CMS_CACHE_DURATIONS = {}


class BackingServices(object):
    DATABASES = values.DatabaseURLValue('sqlite:///_dev/database.db')


class AssetsConfig(object):
    MEDIA_ROOT = values.PathValue(os.path.join(PROJECT_BASE, '_dev', 'media'))
    MEDIA_URL = values.Value('/media/')

    STATIC_ROOT = values.PathValue(os.path.join(PROJECT_BASE, '_dev', 'static'))
    STATIC_URL = values.Value('/static/')

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )


class Config(AssetsConfig, BackingServices, CMSConfig, DebugFlags,
             Configuration):
    # Administrators
    ADMINS = (
        ('Jonathan Stoppani', 'jonathan@stoppani.name'),
    )
    MANAGERS = ADMINS

    # Site identity and basic configuration
    SITE_ID = 1
    ROOT_URLCONF = 'frinat.urls'
    SECRET_KEY = 'trtzz-r^8-0noo-=eq$lh7328f5)xa7?5-@%99*0f#vp7&w2yw' ###
    WSGI_APPLICATION = 'frinat.wsgi.application'

    # Broken links
    APPEND_SLASH = True
    @property
    def SEND_BROKEN_LINK_EMAILS(self):
        return not self.DEBUG

    IGNORABLE_404_ENDS = [
        'favicon.ico',
        'favicon.png',
    ]
    IGNORABLE_404_ENDS += [i + '/' for i in IGNORABLE_404_ENDS]

    # Localization (django)
    LANGUAGE_CODE = 'fr'
    USE_I18N = True
    USE_L10N = True
    LANGUAGES = (
        ('fr', gettext('French')),
        #('de', gettext('German')),
        #('en', gettext('English')),
    )
    TIME_ZONE = 'Europe/Zurich'
    USE_TZ = True
    FIRST_DAY_OF_WEEK = 1  # Monday

    # Templating
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.i18n',
        'django.core.context_processors.request',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'cms.context_processors.media',
        'sekizai.context_processors.sekizai',
    )
    TEMPLATE_DIRS = []

    # Requests processing
    #MIDDLEWARE_CLASSES = (
    #    'django.middleware.cache.UpdateCacheMiddleware',
    #    'django.middleware.cache.FetchFromCacheMiddleware',
    #)
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.doc.XViewMiddleware',
        'django.middleware.common.CommonMiddleware',
        'cms.middleware.page.CurrentPageMiddleware',
        'cms.middleware.user.CurrentUserMiddleware',
        'cms.middleware.toolbar.ToolbarMiddleware',
        'cms.middleware.language.LanguageCookieMiddleware',
    )

    # Applications
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',
        'django.contrib.admindocs',
        'django.contrib.markup',
        'django.contrib.humanize',
        'django.contrib.syndication',
        'django.contrib.sitemaps',
        'django.contrib.staticfiles',

        'south',
        'reversion',

        # CMS
        'cms',
        'mptt',
        'menus',
        'sekizai',

        # CMS plugins
        'cms.plugins.text',
        'cms.plugins.picture',
        'cms.plugins.link',
        'cms.plugins.file',
        'cms.plugins.snippet',
        'cms.plugins.googlemap',

        # Specific apps
        'frinat.frontend',
        'schedule',
        #'tinymce',
        'frinat.sponsors',
        'frinat.calendar',
        #'frinat.people',
        #'filebrowser',

        # Deprecated
        #'tagging',
        #'zinnia',
        #'zinnia.plugins',
    )

    # Editor configuration
    @property
    def TINYMCE_JS_URL(self):
        return os.path.join(self.MEDIA_URL, 'scripts', 'tiny_mce', 'tiny_mce.js')

    @property
    def TINYMCE_JS_ROOT(self):
        return os.path.join(self.MEDIA_ROOT, 'scripts', 'tiny_mce')

    TINYMCE_DEFAULT_CONFIG = {
        'width': 600,
        'height': 400,
        'plugins': "table,spellchecker,paste,searchreplace",
        'theme': "advanced",
        'theme_advanced_toolbar_location' : "top",
        'theme_advanced_toolbar_align' : "left",
        'theme_advanced_buttons3_add' : "tablecontrols",
    }

    # Sessions###
    #SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    #SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    #SESSION_COOKIE_SECURE = True
