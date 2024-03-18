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
    author = AuthorSerializer()  # Include the AuthorSerializer for the 'author' field
    categories = CategorySerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author',
                  'created_at', 'updated_at', 'categories', 'image']

    # Optionally, you can override the to_representation method to customize the serialized data
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = f"{instance.author.user.first_name} {instance.author.user.last_name}"
        representation['categories'] = [
            category.name for category in instance.categories.all()]
        return representation

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     images = representation.pop('images')
    #     content = instance.content

    #     for image in images:
    #         position = image['position']
    #         content = content.replace(
    #             f'{{image_{position}}}', f'<img src="{image["image"]}">')

    #     representation['content'] = content
    #     return representation


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
