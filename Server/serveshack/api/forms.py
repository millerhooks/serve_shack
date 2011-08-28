import re
from django import forms
from datetime import datetime

__all__ = ('PaginationForm', 'TemporalPaginationForm',
        'GeoForm', 'GetCheckInForm', 'PostCheckInForm')

##
# Pagination Forms
###

class BasePaginationForm(forms.Form):
    limit = forms.IntegerField(required=False, min_value=1)

    def clean_limit(self):
        limit = self.cleaned_data['limit']
        self.limit = limit if limit else 10
        return self.limit

    def get_limit(self, max_objects=10):
        return min(max_objects, self.limit)


class PaginationForm(BasePaginationForm):
    page = forms.IntegerField(required=False, min_value=1)

    def clean_page(self):
        page = self.cleaned_data['page']
        return page if page else 1


class TemporalPaginationForm(BasePaginationForm):
    before  = forms.IntegerField(required=False)

    def clean_before(self):
        before = self.cleaned_data['before']
        return before if before else datetime.now()

###
# Geo Forms
##

class GeoForm(forms.Form):
    radius = forms.IntegerField()
    latitude = forms.DecimalField()
    longitude = forms.DecimalField()

    def get_radius(self, max_radius=100):
        return min(max_radius, self.cleaned_data['radius'])

###
# Search
##

class APISearchForm(PaginationForm):
    query = forms.CharField(required=True)

    def clean_query(self):
        normalize = re.compile(r'\s{2,}').sub
        find = re.compile(r'"([^"]+)"|(\S+)').findall

        return [
            normalize(' ', (t[0] or t[1]).strip()) \
                for t in find(self.cleaned_data['query'])
        ]