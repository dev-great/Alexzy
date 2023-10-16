from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_picture = models.ImageField(
        upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    image = models.ImageField(
        upload_to='article_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Image(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='article_images/')
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.image.name


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} - {self.article.title}'
