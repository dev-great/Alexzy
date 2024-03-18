from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from authentication.models import CustomUser


class Author(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField()

    def __str__(self):
        return self.user.email


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Image(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.image.name


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.email

    class Meta:
        ordering = ('-created_at',)
