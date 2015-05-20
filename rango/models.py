from django.db                      import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models     import User

# Create your models here.
class Category(models.Model):
    name  = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug  = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Category(name={}, views={}, likes={}, slug={})>".format \
            (
                self.name, 
                self.views, 
                self.likes,
                self.slug,
            )


class Page(models.Model):
    category = models.ForeignKey(Category)
    title    = models.CharField(max_length=128)
    url      = models.URLField()
    views    = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<Page(category={}, title={}, url={}, views={})>".format \
            (
                self.category,
                self.title, 
                self.url, 
                self.views,
            )


class UserProfile(models.Model):
    # This line is requires. Links UserProfile to User model.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __str__ method to return something meaningful!
    def __str__(self):
        return self.user.username

    def __repr__(self):
        return "<UserProfile(username={})>".format(self.user.username)
        