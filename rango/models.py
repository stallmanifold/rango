from django.db                      import models
from django.template.defaultfilters import slugify


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

