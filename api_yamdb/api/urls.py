from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoriesViewSet, CommentViewSet, GenresViewSet,
                    GettingAToken, ReviewViewSet, TitlesViewSet,
                    UserSignup, UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('categories', CategoriesViewSet, basename='categories')
router.register('genres', GenresViewSet, basename='genres')
router.register('users', UserViewSet, basename='users')
router.register(r'titles', TitlesViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet
)


urlpatterns = [
    path('v1/auth/', include([
        path('signup/', UserSignup.as_view()),
        path('token/', GettingAToken.as_view()),
    ])),
    path('v1/', include(router.urls)),
]
