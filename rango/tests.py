from django.test              import TestCase
from django.core.urlresolvers import reverse

from rango.models             import Category


def add_category(name, views, likes):
    category = Category.objects.get_or_create(name=name)[0]
    category.views = views
    category.likes = likes
    category.save()
    return category


class CategoryMethodsTests(TestCase):

    def test_number_of_views_is_nonnegative(self):
        """
        The test test_number_of_views_is_nonnegative should return True for categories when 
        views are zero or positive.
        """

        category = Category(name='test', views=-1, likes=0)
        category.save()
        self.assertEqual((category.views >= 0), True)


    def test_number_of_likes_is_nonnegative(self):
        """
        The test number_of_views_is_nonnegative should results True for categories where views 
        are zero or positive.
        """

        category = Category(name='test', views=-1, likes=-1)
        category.save()
        self.assertEqual((category.likes >= 0), True)


    def test_slug_line_creation(self):
        """
        slug_line_creation checks to make sure that when we add a category an appropriate slug line is created
        i.e. "Random Category String" -> "random-category-string"
        """

        category = add_category('Random Category String', 1, 1)
        category.save()
        self.assertEqual(category.slug, 'random-category-string')


    def test_category_contains(self):
        """
        test_category_contains tests whether the save() function is working correctly.
        """

        category = Category(name='test', views=21, likes=21)
        category.save()
        self.assertEqual(Category.objects.filter(pk=category.pk).exists(), True)


class IndexViewTests(TestCase):

    def test_index_view_with_no_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])


    def test_index_view_with_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """

        add_category('test',1,1)
        add_category('temp',1,1)
        add_category('tmp',1,1)
        add_category('tmp test temp',1,1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tmp test temp")

        num_cats =len(response.context['categories'])
        self.assertEqual(num_cats , 4)


