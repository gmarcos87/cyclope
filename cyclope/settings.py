#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010-2013 Código Sur Sociedad Civil.
# All rights reserved.
#
# This file is part of Cyclope.
#
# Cyclope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cyclope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Default and dynamic (db based) settings.

CYCLOPE_* settings will be available to templates through the site_settings context processor.

Attributes:

  Overidable by the project settings.py:

    CYCLOPE_PROJECT_PATH: path to the django project that will be serving Cyclope
    CYCLOPE_PREFIX: prefix for Cyclope URLs, defaults to 'cyclope/'

  Automatic (based on database values):

    CYCLOPE_PROJECT_NAME
    CYCLOPE_SITE_SETTINGS: the SiteSettings instance
    CYCLOPE_CURRENT_THEME
    CYCLOPE_THEME_MEDIA_URL
    CYCLOPE_DEFAULT_LAYOUT
    CYCLOPE_DEFAULT_TEMPLATE
    CYCLOPE_CONTACTS_PROFILE_MODULE
    CYCLOPE_CONTACTS_PROFILE_ADMIN_INLINE_MODULE
    CYCLOPE_CONTACTS_PROFILE_TEMPLATE

"""

import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as ugettext
from django.db.models.signals import post_save
from django.core.exceptions import ImproperlyConfigured
from django.db.utils import DatabaseError

from cyclope.models import SiteSettings, DesignSettings

from cyclope.core.frontend.sites import site

CYCLOPE_PREFIX = getattr(settings, 'CYCLOPE_PREFIX', 'cyclope/')

# For backwards compatibility only!
CYCLOPE_STATIC_URL = getattr(settings, 'CYCLOPE_STATIC_URL', settings.STATIC_URL)
CYCLOPE_STATIC_ROOT = getattr(settings, 'CYCLOPE_STATIC_ROOT', settings.STATIC_ROOT)
CYCLOPE_MEDIA_URL =  CYCLOPE_STATIC_URL
CYCLOPE_MEDIA_ROOT = CYCLOPE_STATIC_ROOT

CYCLOPE_TEXT_STYLE = getattr(settings, 'CYCLOPE_TEXT_STYLE', 'textile')

# For backwards compatibility only!
CYCLOPE_ARTICLE_TEXT_STYLE = getattr(settings, 'CYCLOPE_TEXT_STYLE', 'textile')
CYCLOPE_STATICPAGE_TEXT_STYLE = getattr(settings, 'CYCLOPE_TEXT_STYLE', 'textile')

# Contacts Profile
CYCLOPE_CONTACTS_PROFILE_MODULE = getattr(settings, 'CYCLOPE_CONTACTS_PROFILE_MODULE', None)
CYCLOPE_CONTACTS_PROFILE_ADMIN_INLINE_MODULE = getattr(settings, 'CYCLOPE_CONTACTS_PROFILE_ADMIN_INLINE_MODULE', None)
CYCLOPE_CONTACTS_PROFILE_TEMPLATE = getattr(settings, 'CYCLOPE_CONTACTS_PROFILE_TEMPLATE', None)

# pagination
CYCLOPE_PAGINATION = getattr(settings, 'CYCLOPE_PAGINATION',
                             { 'TEASER' : 5,
                               'LABELED_ICON' : 30,
                               'FORUM' : 30,
                               'DETAIL' : 9999,
                               })
CYCLOPE_RSS_LIMIT = 50

# Feed

CYCLOPE_FEED_CACHE_TIME = getattr(settings, 'CYCLOPE_FEED_CACHE_TIME', 600)

CYCLOPE_PROJECT_PATH = getattr(settings, 'CYCLOPE_PROJECT_PATH', None)

if not CYCLOPE_PROJECT_PATH:
    raise ImproperlyConfigured(
        ugettext('You need to set the CYCLOPE_PROJECT_PATH in your settings file.'))
# we normalize the path
CYCLOPE_PROJECT_PATH = os.path.normpath(CYCLOPE_PROJECT_PATH)

CYCLOPE_PROJECT_NAME = os.path.basename(CYCLOPE_PROJECT_PATH)

CYCLOPE_BASE_CONTENT_TYPES = site.base_content_types

# SINGLE jQuery VERSION - updatable application-wide
# django jquery is outdated in v.1.4, latest even uses jQv.3! jQv.1.9+ is still IE8 compatible
CYCLOPE_JQUERY_PATH = "js/jquery-1.12.4.min.js"
# backwards compatibility
CYCLOPE_JQUERY_MIGRATE_PATH = 'js/jquery-migrate-1.4.1.min.js'
# jQuery UI
CYCLOPE_JQUERY_UI_PATH = 'js/jquery-ui-1.11.4-min.js'
CYCLOPE_JQUERY_UI_CSS_PATH = 'css/jquery-ui-1.11.4-min.css'


import themes

def get_site_settings():
    """Get the SiteSettings object.

    Returns:
        SiteSettings instance or None if no SiteSettings have been created.

    """
    try:
        # a Cyclope project is supposed to have only one SiteSettings object
        site_settings = SiteSettings.objects.get()
    # catch exceptions if no settings are created
    except:
        site_settings = None
    return site_settings

def populate_from_site_settings(site_settings):
    # Read some settings and make them available at module level
    CYCLOPE_SITE_SETTINGS = site_settings
    CYCLOPE_BASE_URL = "http://" + CYCLOPE_SITE_SETTINGS.site.domain # FIXME: could be https
    CYCLOPE_CURRENT_THEME = CYCLOPE_SITE_SETTINGS.theme
    CYCLOPE_THEME_TYPE = getattr(themes.get_theme(CYCLOPE_CURRENT_THEME), 'theme_type', 'classic')
    CYCLOPE_SEARCH_DATE = CYCLOPE_SITE_SETTINGS.enable_search_by_date
    
    if CYCLOPE_CURRENT_THEME in themes.get_local_themes():
        CYCLOPE_THEME_MEDIA_URL = '%s%s/' % (
            settings.CYCLOPE_LOCAL_THEMES_MEDIA_PREFIX, CYCLOPE_CURRENT_THEME)
    else:
        CYCLOPE_THEME_MEDIA_URL = '%sthemes/%s/' % (settings.STATIC_URL,
                                                    CYCLOPE_CURRENT_THEME)

    CYCLOPE_THEME_PREFIX = 'cyclope/themes/%s/' % CYCLOPE_CURRENT_THEME
    CYCLOPE_THEME_BASE_TEMPLATE = 'cyclope/themes/%s/base.html' % CYCLOPE_CURRENT_THEME

    if CYCLOPE_SITE_SETTINGS.default_layout_id:
        try:
            CYCLOPE_DEFAULT_LAYOUT = CYCLOPE_SITE_SETTINGS.default_layout

            CYCLOPE_DEFAULT_TEMPLATE = 'cyclope/themes/%s/%s' % (
                CYCLOPE_CURRENT_THEME,
                CYCLOPE_DEFAULT_LAYOUT.template)

        # TODO(nicoechaniz): fix this workaround. It's here for migrations on the
        # Layout model, which fail to complete with a DatabaseError when this
        # module is imported. Eg: cyclope/migrations/0011...
        except DatabaseError:
            pass

    # Update the settings module with the settings
    for name, value in locals().copy().iteritems():
        if name.startswith("CYCLOPE"):
            globals()[name] = value

CYCLOPE_SITE_SETTINGS = get_site_settings()
populate_from_site_settings(CYCLOPE_SITE_SETTINGS)

def _refresh_site_settings(sender, instance, created, **kwargs):
    "Callback to refresh site settings when they are modified in the database"
    # we remove our keys from globals, otherwise deleted db_based settings don't
    # get deleted at module level
    if not kwargs.get('raw', True):
        cyc_keys = [ key for key in globals() if key.startswith('CYCLOPE')]
        for key in cyc_keys:
            globals().pop(key)
        import sys
        reload(sys.modules[__name__])

post_save.connect(_refresh_site_settings, sender=SiteSettings)
post_save.connect(_refresh_site_settings, sender=DesignSettings)
