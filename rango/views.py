from django.shortcuts       import render
from django.http            import HttpResponse
from django.template.loader import get_template
from django.template        import Context, RequestContext
from rango.models           import Category, Page
from rango.forms            import CategoryForm, PageForm


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = \
        {
            'categories': category_list,
            'pages': page_list, 
        }

    # Render the response and send it back!
    return render(request, 'rango/index.html', context_dict)


def about(request):
    context = Context({'descriptor': "ABOUT"})
    template = get_template('rango/about.html')
    return HttpResponse(template.render(context))


def category(request, category_name_slug):
    # Create a context dictional which we can pass to the template rendering engine.
    context_dict = Context({})

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() metho returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note the filters returns >= 1 model instances.
        pages = Page.objects.filter(category=category)

        # Adds our result list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category']= category
        context_dict['category_name_slug'] = category.slug
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contains errors. Just print them to the terminal.
            print(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    # We need to use a RequestContext here since Django requires all
    # forms that use the 'POST' method in request have a csrf token. The RequestContext
    # retains the original request containing the csrf token. The Context class does not,
    # so when the form data is submitted to Django, it throws a 403 error since it detects
    # the csrf cookie as being not set.
    context = RequestContext(request, {'form': form})
    return render(request, 'rango/add_category.html', context)


def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print(form.errors)
    else:
        form = PageForm()

    context = RequestContext(request, {'form': form, 'category': cat, })

    return render(request, 'rango/add_page.html', context)