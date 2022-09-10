from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Avg
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, status,
                            viewsets)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from reviews.models import Categories, Comments, Genres, Review, Title, User
from .filter import Titlefilter
from .permissions import Me, MeAdmin, ReadOrAdmin, WriteOwnerOrPersonal
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, MeSerializer, ReviewSerializer,
                          TitlesCreateSerializer, TitlesSerializer,
                          UserSerializer, UserSignupSerializer,
                          GettingATokenSerializer)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (ReadOrAdmin,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ('category', 'genre', 'name', 'year',)
    filterset_class = Titlefilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitlesCreateSerializer
        return TitlesSerializer


class ListCreateViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin,
                        mixins.CreateModelMixin, viewsets.GenericViewSet):

    pass


class CategoriesViewSet(ListCreateViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ReadOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(ListCreateViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ReadOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class UserSignup(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = get_object_or_404(User, username=request.data['username'])
        default_token_generator = PasswordResetTokenGenerator()
        token = default_token_generator.make_token(user)
        send_mail('confirmation_code',
                  token,
                  'webmaster@localhost',
                  [serializer.validated_data['email'], ])
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


class GettingAToken(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GettingATokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data['username']
        token = request.data['confirmation_code']
        user = get_object_or_404(User, username=username)
        token_check = PasswordResetTokenGenerator()
        if token_check.check_token(user, token):
            access_refresh = RefreshToken.for_user(user)
            data = {"token": access_refresh}
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response('передан некорректный токен',
                            status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [WriteOwnerOrPersonal]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return super().get_queryset().filter(
            title_id=self.kwargs['title_id']
        )

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(
            title=title,
            author=self.request.user
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [WriteOwnerOrPersonal]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return super().get_queryset().filter(
            review_id=self.kwargs['review_id']
        )

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        serializer.save(
            review=review,
            author=self.request.user
        )


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (MeAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['get', 'patch'], permission_classes=[Me])
    def me(self, request):
        username = request.user
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = MeSerializer(user, many=False)
        return Response(serializer.data)
