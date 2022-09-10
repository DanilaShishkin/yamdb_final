from django_filters import rest_framework as filter

from reviews.models import Title


class Titlefilter(filter.FilterSet):
    category = filter.CharFilter(field_name='category__slug')
    genre = filter.CharFilter(field_name='genre__slug')
    name = filter.CharFilter(field_name='name', lookup_expr='icontains')
    year = filter.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ['name', 'category', 'genre', 'year']
