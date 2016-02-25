from datetime                       import datetime
from django.shortcuts               import render, redirect
from django.http                    import HttpResponse, HttpResponseRedirect
from django.template.loader         import get_template
from django.template                import Context, RequestContext
from django.contrib.auth            import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.query         import QuerySet
from rango.models                   import Category, Page, UserProfile, User
from rango.forms                    import CategoryForm, PageForm
from rango.forms                    import UserForm, UserProfileForm
from rango.forms                    import PasswordChangeForm


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    # Does the cookie last_visit exist?
    if last_visit is not None:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it has been more than a day since the last visit
        if (datetime.now() - last_visit_time).seconds > 0:
            visits += 1
            # ... and flag that the cookie last visit needs to be updated
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so flag that it should be set.
        reset_last_visit_time = True

    # Append the new cookie information if we visited previously.
    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    
    context_dict['visits'] = visits
    context = RequestContext(request, context_dict)
    template = get_template('rango/index.html')
    response = HttpResponse(template.render(context))
    
    return response


def about(request):
    context_dict = {'descriptor': 'ABOUT'}
    if request.session.has_key('visits'):
        visits = request.session.get('visits')
    else:
        visits = 1

    last_visit = request.session.get('last_visit')
    # Does the cookie last_visit exist?
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it has been more than a day since the last visit
        if (datetime.now() - last_visit_time).seconds > 0:
            visits += 1
            # ... and flag that the cookie last visit needs to be updated
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so flag that it should be set.
        reset_last_visit_time = True

    # Append the new cookie information if we visited previously.
    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits

    context_dict['visits'] = visits
    context = RequestContext(request, context_dict)
    template = get_template('rango/about.html')

    return HttpResponse(template.render(context))


def category(request, category_name_slug):
    # Create a context dictional which we can pass to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() metho returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        pages = list(Page.objects.filter(category=category).order_by('-views'))

        # Adds our result list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
        context_dict['category_name_slug'] = category.slug
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        print(category_name_slug)
        context_dict['category_name_slug'] = category_name_slug

    if request.method == 'POST':
        # We don't have to use bing if we don't want to.
        query = request.POST.get('query', '')
        if query != '':
            pages = context_dict.get('pages', [])
            # search_results = list(run_query(query))
            search_results = list(filter(lambda page: query in page.title, pages))
            context_dict['pages'] = search_results  

        context = RequestContext(request, context_dict)
    # Treat request as a 'GET'    
    else:
        context = RequestContext(request, context_dict)

    return render(request, 'rango/category.html', context)


@login_required
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


@login_required
def like_category(request, category_id):
    
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        category = None

    if request.method == 'GET':
        if category:
            #Update the number of likes for category
            category.likes += 1
            category.save()
            likes = category.likes
        else:
            # Category does not exist.
            likes = 0

        return HttpResponse("{} likes".format(likes))    


@login_required
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

    context = RequestContext(request, {'form': form, 'category': cat})

    return render(request, 'rango/add_page.html', context)


def register(request):
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    context = RequestContext \
        (
            request, 
            {
                'user_form': user_form,
                'profile_form': profile_form, 
                'registered': registered
            }
        )

    return render(request, 'rango/register.html', context)


def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            # Insert error message into response and put the response on the 
            # login page populated with and error message.
            context = RequestContext \
                (
                    request, 
                    {
                        'login_error': 'Invalid username or password.',
                        'old_username': username,
                    }
                )
            template = get_template('rango/login.html')
            return HttpResponse(template.render(context))

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')


#TODO: Refactor this function to take the password vierification logic out of the view.
@login_required
def change_password(request):

    def prepare_form(form):
        new_form = PasswordChangeForm({'username': form['username'].value()})
        for field, error_list in form.errors.items():
            for error in error_list:
                new_form.add_error(field, error)

        return new_form


    if request.method == 'POST':
        password_change_form = PasswordChangeForm(request.POST)

        if password_change_form.is_valid():
            username = password_change_form['username'].value()
            password = password_change_form['old_password'].value()
            user = authenticate(username=username, password=password)
            # User has been authenticated, so it is safe to change the password.
            if user:
                new_password = password_change_form['new_password'].value()
                user.set_password(new_password)
                user.save()
                # Redirect to password change complete page.
                template = get_template('rango/password_change_complete.html')
                context = RequestContext(request, {})
                return HttpResponseRedirect('password_change_complete')
            # User entered the wrong password, or needs to register.
            else:
                print(password_change_form.errors)
                password_change_form = prepare_form(password_change_form)
        # Return the password change form displaying errors.
        else:
            print(password_change_form.errors)
            password_change_form = prepare_form(password_change_form)
    # The request method is not POST, so return the password form.
    else:
        password_change_form = PasswordChangeForm()
        
    template = get_template('rango/password_change_form.html')
    context = RequestContext(request, {'password_change_form': password_change_form})
    return HttpResponse(template.render(context))


def password_change_complete(request):
    context = RequestContext(request, {})
    template = get_template('rango/password_change_complete.html')
    response = HttpResponse(template.render(context))

    return response


def track_url(request, page_id):
    page = None
    url = 'index'
    if request.method== 'GET':
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            page = None

        if page:
            page.views += 1
            page.save()
            url = page.url
        else:
            return redirect('index')

    return redirect(url)


def registration_complete(request):
    context = RequestContext(request, {})
    template = get_template('registration/registration_complete.html')
    response = HttpResponse(template.render(context))

    return response


@login_required
def profile(request):
    if request.method == 'GET':
        user = request.user
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile()
    else:
        user = request.user
        user_profile = UserProfile()
    
    context_dict = \
        {
            'user_profile': user_profile, 
            'username': user.username,
            'website': user_profile.website,
            'picture_url': user_profile.picture.url,
        }

    context = RequestContext(request, context_dict)
    template = get_template('rango/profile.html')
    print(context['picture_url'])
    return HttpResponse(template.render(context))


@login_required
def edit_profile(request):
    # Grab the user's information from the database, if it exists.
    try:
        user = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        user = User() 

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)

    # Profile Update submission.
    if request.method == 'POST':
        # Grab the user's information from the database.

        form = UserProfileForm(data=request.POST, instance=profile)
        if user and form.is_valid():
            # Update the user's profile.
            # form.save(commit=True)
            profile = form.save(commit=False)
            profile.picture = request.FILES.get('picture')
            profile.save()
            # Prepare the return response
            response = redirect('profile_edit_complete')
        else:
            # User does not exist in database. We will redirect the user
            # to the registration page.
            response = redirect('registration_register')
    # Visiting the profile page.
    else:
        # Get user profile data and populate the form.
        form = UserProfileForm(instance=profile)
        print(form)

        context_dict = \
            {
                'username': user.username, 
                'user': user, 
                'website': profile.website, 
                'picture_url': profile.picture.url,
                'user_profile_form': form,
            }
        context = RequestContext(request, context_dict)
        response = render(request, 'rango/edit_profile.html', context)

    return response


def profile_edit_complete(request):
    context = RequestContext(request, {})
    template = get_template('rango/profile_edit_complete.html')
    response = HttpResponse(template.render(context))

    return response


def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
            cat_list = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
            if len(cat_list) > max_results:
                cat_list = cat_list[:max_results]

        return cat_list


def suggest_category(request, max_results=8):

        cat_list = []
        starts_with = ''
        if request.method == 'GET':
            starts_with = request.GET['suggestion']

        cat_list = get_category_list(max_results, starts_with)
        context = RequestContext(request, {'cat_list': cat_list })

        return render(request, 'rango/category_list.html', context)


