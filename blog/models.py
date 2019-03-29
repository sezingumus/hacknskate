from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save,post_save
from django.contrib.auth.models import User
from django.db import models
import datetime

from uuid import uuid4

# Create your models here.
from blog.utils import unique_slug_generator
# Create your models here.
def create_id():
    now = datetime.datetime.now()
    return str(now.year) + str(now.month) + str(now.day) + str(uuid4())[:7]

class Blog(models.Model):
    #id                      = models.CharField(max_length=20,primary_key=True, default=create_id, editable=False)
    author                  = models.CharField(max_length=20,default='Sezin')
    title                   = models.CharField(max_length=200)
    text                    = models.TextField()
    published_date          = models.DateField(default=timezone.now)
    updated_date            = models.DateField(blank=True, null=True)
    like                    = models.IntegerField(default=0)
    category                = (('A', 'All'), ('C', 'CyberSecurity'), ('I', 'ComputerScience'), ('S', 'Skate'), ('O', 'Other'))
    blog_category           = models.CharField(max_length=1, choices=category, default='C')
    image                   = models.ImageField(upload_to='images/')
    blog_pdf                = models.FileField(upload_to='blogs',null=True)
    slug                    = models.SlugField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return ('blog_detail',(),{'slug':self.slug})


def blog_pre_save_receiver(sender, instance, *args, **kwargs):
    print('saving')
    print(instance.published_date)
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(blog_pre_save_receiver,sender=Blog)


class Reference(models.Model):
    name                    = models.CharField(max_length=100)
    surname                 = models.CharField(max_length=100)
    company                 = models.CharField(max_length=100)
    department              = models.CharField(max_length=50)
    email                   = models.EmailField(max_length=20)

class Comment(models.Model):

    blog                    = models.ForeignKey(Blog,on_delete=models.CASCADE, related_name='comments')
    name                    = models.CharField(max_length=20)
    email                   = models.EmailField(max_length=30)
    created_date            = models.DateTimeField(default=timezone.now)
    content                 = models.TextField(max_length=2000,blank=True,null=True,default='')


    def approve(self):

        self.created_date     = timezone.now()
        self.save()

    def __str__(self):
        return self.content
