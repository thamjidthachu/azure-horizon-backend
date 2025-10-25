from rest_framework import serializers

from apps.authentication.serializers import UserSerializer
from .models import File, Service, Comment, Advertisement


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'images']
        read_only_fields = ['images']

class ServiceListSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True, source='file_set')
    rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['slug', 'name', 'price', 'unit', 'time', 'files','synopsis', 'rating', 'review_count',]

    @staticmethod
    def get_rating(obj):
        reviews = obj.service_comment.all()
        if reviews.exists():
            total_rating = sum([review.rating for review in reviews])
            return total_rating / reviews.count()
        return 0

    @staticmethod
    def get_review_count(obj):
        return obj.service_comment.count()

class ServicesSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True, source='file_set')
    rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['slug', 'create_time']

    @staticmethod
    def get_rating(obj):
        reviews = obj.service_comment.all()
        if reviews.exists():
            total_rating = sum([review.rating for review in reviews])
            return total_rating / reviews.count()
        return 0

    @staticmethod
    def get_review_count(obj):
        return obj.service_comment.count()

    @staticmethod
    def get_reviews(obj):
        comments = obj.service_comment.all()
        return CommentsSerializer(comments, many=True).data if comments.exists() else None


class CommentsSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['author', 'message', 'rating', 'created_at']


class AdvertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ['title', 'file', 'link']
