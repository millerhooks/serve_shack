from piston.handler import BaseHandler
from piston.utils import rc, validate, FormValidationError

from django.db.models import Q
from django.contrib.gis.measure import D

from venues.models import Venue
from api.forms import PaginationForm, APISearchForm, GeoForm

from django.core.paginator import Paginator, EmptyPage, InvalidPage

from piston.handler import BaseHandler

##
# Handler Base
###

class PandaBaseHandler(BaseHandler):
    def paginate(self, queryset, page=1, objects_per_page=10):
        paginator = Paginator(queryset, objects_per_page)

        try:
            page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)
        return page

    def get_response_dict(self, ret):
        return { 'result': ret, 'error': None }

    def _get_pagination_dict(self, page):
        if page:
            return {
                'total_objects': page.paginator.count,
                'objects_per_page': page.paginator.per_page,
                'has_next': page.has_next(),
                'has_previous': page.has_previous(),
                'current_page': page.number,
                'num_pages': page.paginator.num_pages
            }

        return None

    def get_paginated_response_dict(self, page, ret):
        ret = self.get_response_dict(ret)
        ret['paginator'] = self._get_pagination_dict(page)
        return ret


class TwistedSouthBaseHandler(PandaBaseHandler):
    def venue_to_dict(self, venue):
        return {
            'id': venue.id,
            'name': venue.name,
            'address1': venue.address1,
            'address2': venue.address2,
            'city': venue.city,
            'state': venue.state,
            'zip_code': venue.zip_code,
            'phone_number': venue.phone_number,
            'email': venue.email,
            'url': venue.url,
            'hours_ops': venue.hours_ops,
            'rating': venue.rating,
            'video_type': venue.video_type,
            'video_url': venue.video_url,
            'facebook_url': venue.facebook_url,
            'twitter_url': venue.twitter_url,
            'map_url': venue.map_url,
            'internal_review': venue.internal_review,
            'internal_review_by': venue.internal_review_by,
            'internal_review_on': venue.internal_review_on,
            'is_featured': venue.is_featured,
            'tags': venue.tags,
            'slug': venue.slug,
            'image': venue.image,
        }

    def lightmap_to_dict(self, lightmap):
        return {
            'id': lightmap.id,
            'name': lightmap.name,
            'map': lightmap.map,
            'radius': lightmap.radius,
            'location': lightmap.location,
            'latitude': lightmap.latitude,
            'longitude': lightmap.longitude,
            'expires': lightmap.expires,
            'created': lightmap.created,
            'modified': lightmap.modified,
        }

###
# Helper for Geo Queries
##
def point(longitude, latitude):
    return fromstr(
        'POINT(%s %s)' % (longitude, latitude,), srid=settings.DEFAULT_SRID
    )

###
# Handlers
##

class VenueHandler(TwistedSouthBaseHandler):
    allowed_methods = ('GET', 'POST')

    @validate(PaginationForm, 'GET')
    def read(self, request):
        import pdb; pdb.set_trace()
        pagination_form = request.form
        queryset = Venue.objects.all()

        page = self.paginate(
            queryset,
            page=pagination_form.cleaned_data['page'],
            objects_per_page=pagination_form.get_limit(25)
        )

        venues = list(page.object_list)

        return self.get_paginated_response_dict(page, [
            self.venue_to_dict(venue,) \
                for venue in venues
        ])

class VenueSearchHandler(TwistedSouthBaseHandler):
    allowed_methods = ('GET')

    @validate(PaginationForm, 'GET')
    def read(self, request):
        pagination_form = request.form
        geo_form = GeoForm(request.GET)
        search_form = APISearchForm(request.GET)

        queryset = Venue.objects.all()

        if geo_form.is_valid():
            queryset = queryset.filter(venue__coordinates__distance_lte=(
                point(
                    geo_form.cleaned_data['longitude'],
                    geo_form.cleaned_data['latitude'],
                ),
                D(mi=geo_form.get_radius(max_radius=100))
            ))
        #elif not search_form.is_valid():
        #    raise FormValidationError(geo_form)

        if search_form.is_valid():
            search_query = ' '.join(search_form.cleaned_data['query'])
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(lineup_denorm__icontains=search_query) |
                Q(venue__name__icontains=search_query)
            )

        page = self.paginate(
            queryset,
            page=pagination_form.cleaned_data['page'],
            objects_per_page=pagination_form.get_limit(25)
        )

        tags = list(page.object_list)

        return self.get_paginated_response_dict(page, [
            self.venue_to_dict(tags,) \
                for tag in tags
        ])

