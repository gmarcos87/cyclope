# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _
from feincms.admin import editor

from cyclope.models import *
from cyclope.forms import StaticPageAdminForm,\
                          MenuItemAdminForm,\
                          BaseContentAdminForm,\
                          SiteSettingsAdminForm,\
                          LayoutAdminForm,\
                          RegionViewInlineForm
from cyclope.core.collections.admin import CollectibleAdmin



class BaseContentAdmin(admin.ModelAdmin):
    # updates related menu_items information when a BaseContent is saved
    form = BaseContentAdminForm
    def save_model(self, request, obj, form, change):
        selected_items_ids = form.data.getlist('menu_items')
        selected_items = set(MenuItem.objects.filter(pk__in=selected_items_ids))
        old_items = set(MenuItem.objects.filter(content_object=obj))
        discarded_items = old_items.difference(selected_items)
        new_items = selected_items.difference(old_items)
        for menu_item in discarded_items:
            menu_item.content_type = None
            menu_item.content_object = None
            menu_item.content_view = None
            menu_item.save()
        for menu_item in new_items:
            menu_item.content_type = ContentType.objects.get_for_model(obj)
            menu_item.content_object = obj
            menu_item.save()
        super(BaseContentAdmin, self).save_model(request, obj, form, change)

admin.site.register(BaseContent, BaseContentAdmin)

class MenuItemAdmin(editor.TreeEditor):
    form = MenuItemAdminForm
#    readonly_fields = ['content_object']
    raw_id_fields = ['content_object']
    fieldsets = ((None,
                  {'fields': ('menu', 'parent', 'name', 'custom_url',
                              'layout', 'active')}),
                 (_('content details'),
                  {'classes': ('collapse',),
                  'fields':('content_type', 'content_view', 'content_object')})
                )
    list_filter = ('menu',)

admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Menu)

from django import forms
from cyclope.widgets import WYMEditor

class StaticPageAdmin(CollectibleAdmin, BaseContentAdmin):
    form = StaticPageAdminForm

admin.site.register(StaticPage, StaticPageAdmin)

class RegionViewInline(admin.StackedInline):
    form = RegionViewInlineForm
#    template = "admin/cyclope/regionview/stacked_inline.html"
    raw_id_fields = ['content_object']
    model = RegionView
    # ToDo: extra should be 1 or 0 but we are using 2 here to be able to test this until we fix the chainedSelect registry for dinamically added formsets. See ToDo note in templates/admin/cyclope/layout/change_form.html
    extra = 2

class LayoutAdmin(admin.ModelAdmin):
    form = LayoutAdminForm
    inlines = (RegionViewInline, )

admin.site.register(Layout, LayoutAdmin)

class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm

admin.site.register(SiteSettings, SiteSettingsAdmin)
