#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.contrib import admin 
from django.db.models.signals import post_save

from . import models
from . import utils

class ApiFieldInline(admin.TabularInline):
    model = models.ApiField

class ApiModelAdmin(admin.ModelAdmin):
    inlines = [ApiFieldInline]

admin.site.register(models.ApiModel, ApiModelAdmin)

# Go through all the current loggers in the database, and register an admin
for survey in models.ApiModel.objects.all():
    utils.reregister_in_admin(admin.site, survey.Response)

# Update definitions when they change
def survey_post_save(sender, instance, created, **kwargs):
    utils.reregister_in_admin(admin.site, instance.Response)
post_save.connect(survey_post_save, sender=models.ApiModel)

