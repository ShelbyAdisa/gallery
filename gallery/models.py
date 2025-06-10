from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Photo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/')
    tags = models.ManyToManyField(Tag, blank=True)  # Link to Tag model
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class PhotoLike(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    user = models.CharField(max_length=100)  # or ForeignKey to User model
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('photo', 'user')

class PhotoDislike(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    user = models.CharField(max_length=100)  # or ForeignKey to User model
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('photo', 'user')