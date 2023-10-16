from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Author
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image', 'position')


class ArticleSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'author', 'created_at', 'images')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        images = representation.pop('images')
        content = instance.content

        for image in images:
            position = image['position']
            content = content.replace(
                f'{{image_{position}}}', f'<img src="{image["image"]}">')

        representation['content'] = content
        return representation


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
