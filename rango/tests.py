from django.test              import TestCase
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.db.utils          import IntegrityError
from django.db                import transaction

from rango.models             import Category, Page


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


    def test_empty_category_should_have_blank_name_and_blank_slug(self):

        category = Category()
        category.save()
        self.assertEqual(category.name, '')
        self.assertEqual(category.slug, '')


    def test_category_names_should_be_unique(self):
        
        category1 = Category(name='test', views=1, likes=1)
        category2 = Category(name='test', views=2, likes=2)
        category1.save()
        with self.assertRaises(IntegrityError):
            category2.save()


    def test_category_slug_should_be_unique(self):
        
        category1 = Category(name='test1', views=1, likes=1)
        category2 = Category(name='test1', views=2, likes=2)
        category3 = Category(name='test2', views=3, likes=3)
        category1.save()
        
        try:
            with transaction.atomic():
                category2.save()
        except IntegrityError as ie:
            self.assertEqual(category1.slug, category2.slug)
        else:
            self.fail()

        # Saving two different database entries in succession should not
        # raise an error.
        try:
            with transaction.atomic():
                category3.save()
        except IntegrityError as ie:
            self.fail(ie)
        
        self.assertNotEqual(category1.slug, category3.slug)


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


class PageMethodsTests(TestCase):

    def test_page_contains(self):
        """
        test_category_contains tests whether the save() function is working correctly.
        """

        category = Category()
        category.save()
        page = Page(category=category, title='test page', views=21)
        page.save()
        self.assertEqual(Page.objects.filter(pk=page.pk).exists(), True)


    def test_page_views_should_be_nonnegative(self):

        category = Category()
        category.save()
        page = Page(category=category, title='test page', views=-100)
        page.save()
        self.assertTrue(page.views >= 0)


class AboutViewTests(TestCase):

    def test_about_view_exists(self):
        """
        The about page's URL should exists with the specified name in
        the url configuration.
        """

        response = self.client.get(reverse('about'))
        self.assertNotEqual(response.status_code, 404)


    def test_about_view_should_contain_visit_amount(self):
        """
        The about page should contain the number of visits that a user visited
        the about page in its response.
        """

        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        visits = response.context['visits']
        self.assertIsNotNone(visits)
        self.assertTrue(visits > 0)


    def test_about_view_should_contain_descriptor(self):
        """
        The about page should contain the a descriptor for the website in the about
        page response.
        """

        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['descriptor'], 'ABOUT')


class CategoryViewTests(TestCase):

    def test_category_that_does_not_exist(self):
        """
        Test that rango responds correctly when the user tries to 
        go to a category that does not exist.
        """

        # We don't want to save the category because we are interested in 
        # what the view does with a nonexistent category.
        category = Category(name='non_existent_test_category')
        category.slug = category.name
        # If the URL resolver throws an exception, just fail fast.
        try:
            response = self.client.get(reverse('category', args=(category.slug,)))
        except NoReverseMatch as nrm:
            self.fail(msg="The category slug that caused failure is: {}\n \
                {}".format(category.slug, nrm))
        # We should get a HTTP 200 on a non-existent category.
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Category Does Not Exist")
        self.assertContains(response, 
            "The specified category <strong>{}</strong> does not exist!".format(category.slug))


    def test_category_with_empty_name_should_display_does_not_exist_page(self):
        """
        This test tests how rango reacts to trying to render a category with an empty name.
        """

        category = Category(name='')
        category.slug=category.name
        try:
            response = self.client.get(reverse('category', args=(category.slug,)))
        except NoReverseMatch as nrm:
            self.fail(msg="The category slug that caused failure is: {}\n \
                {}".format(category.slug, nrm))
        # We should get a HTTP 200 on a non-existent category.
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Category Does Not Exist")
        self.assertEqual('', category.slug)


    def test_category_with_no_pages(self):
        """
        This test checks that rango displays the correct message
        when no pages are present in a category with no pages.
        """

        category = Category(name='test')
        category.save()

        response = self.client.get(reverse('category', args=(category.slug,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No pages currently in category.")
        