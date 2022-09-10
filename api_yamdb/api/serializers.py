import datetime as dt

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import (Categories, Comments, Genres, Review,
                            Title, User)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genres
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Categories
        fields = ('name', 'slug')


class TitlesCreateSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        many=True,
        queryset=Genres.objects.all(),
        slug_field='slug',
        required=True
    )
    category = SlugRelatedField(
        queryset=Categories.objects.all(),
        slug_field='slug',
        required=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title

    def validate_year(self, value):
        if dt.date.today().year < value:
            raise serializers.ValidationError(
                'Проверьте год создания произведения')
        return value


class TitlesSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year',
                  'rating', 'description',
                  'genre', 'category')
        model = Title


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']
        model = User


class UserSignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def validate_username(self, name):
        if name == "me":
            raise serializers.ValidationError(
                'Пользователя с ником me запрещено создавать'
            )
        return name

    class Meta:
        fields = ['username', 'email']
        model = User


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        exclude = ('title',)

    def validate(self, data):
        request = self.context.get('request')
        if request.method == "POST":
            reviews = Review.objects.filter(
                author=request.user.id,
                title=request.parser_context.get('kwargs').get('title_id'),
            )

            if reviews.exists():
                raise serializers.ValidationError(
                    'Автор может оставлять только один отзыв '
                    'на определённое произведение'
                )

        return data

    def validate_score(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Значение score должно быть больше либо равно 1!'
            )

        if value > 10:
            raise serializers.ValidationError(
                'Значение score должно быть меньше либо равно 10!'
            )

        return value


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date')


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']
        model = User
        read_only_fields = ['role']


class GettingATokenSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['username']
        model = User
