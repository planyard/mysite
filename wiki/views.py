# Required imports
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.http.response import Http404
from .models import Page, UserFile
from .forms import FileUploadForm
from django.contrib.auth import views as auth_views, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from os.path import split

def register_page(request):
    '''Function-based view for user registration'''

    # If the user got here via POST:
    if request.method == 'POST':
        # Create a variable containing a UserCreationForm with the content of the POST.
        form = UserCreationForm(request.POST)
        # If the form variable is valid:
        if form.is_valid():
            # Create username and password variables containing cleaned data of the entered username and password,
            # where 'cleaned data' ensures the data is the correct type (in this case, strings).
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # Create a variable containing a user creation with the credentials provided by the user:
            user = User.objects.create_user(username=username, password=password)
            # Save the user and therefore store it in the database:
            user.save()
            # Authenticate the user:
            user = authenticate(request, username=username, password=password)
            # Log the user in:
            login(request, user)
            # Then, redirect to the index with the user now registered and logged in.
            return redirect('wiki:index')
    # Else, if the user did not arrive via POST:
    else:
    # Create a variable containing a UserCreationForm with no added content:
        form = UserCreationForm()
    # Then, render the 'create_user' template with the content of the form.
    return render(request, 'wiki/create_user.html', {'form': form})


class WikiLoginView(auth_views.LoginView):
    '''Class-based view for logging in'''

    # Modifies the 'get_context_data' method as follows:
    def get_context_data(self, **kwargs):
        # Defines a variable containing all context data
        context = super().get_context_data(**kwargs)
        # If the user is authenticated:
        if self.request.user.is_authenticated:
            # Set an 'auth' context to 'auth':
            context['auth'] = 'auth'
        # Then, return the context.
        return context

    # Points to the correct template
    template_name = 'wiki/login.html'


class WikiLogoutView(auth_views.LogoutView):
    '''Class-based view for logging out'''

    def get_next_page(self):
        return reverse('wiki:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['auth'] = 'auth'
        return context


class IndexView(generic.ListView):
    '''Class-based view for the index'''

    # Points to the correct template
    template_name = 'wiki/index.html'
    # Defines a context object name for reference in the 'index' template
    context_object_name = 'pages'
    # Modifies the 'get_queryset' method to return all pages, ordered by page name
    def get_queryset(self):
        return Page.objects.all().order_by('page_name')
    # Modifies the 'get_context_data' method as follows:
    def get_context_data(self, **kwargs):
        # Defines a variable containing all context data
        context = super().get_context_data(**kwargs)
        # Defines a 'client' context with a request for displaying browser data
        context['client'] = self.request.META['HTTP_USER_AGENT']
        # If the user is authenticated:
        if self.request.user.is_authenticated:
            # Set an 'auth' context to 'auth':
            context['auth'] = 'auth'
        # Then, return the context.
        return context


class PageView(generic.DetailView):
    '''Class-based view for pages'''

    # Retrieves the correct model
    model = Page
    # Points to the correct template
    template_name = 'wiki/page.html'
    # Defines a context object name for reference in the 'page' template
    context_object_name = 'this_page'
    # Modifies the 'get_context_data' method as follows:
    def get_context_data(self, **kwargs):
        # Defines a variable containing all context data
        context = super().get_context_data(**kwargs)
        # If the user is authenticated,
        if self.request.user.is_authenticated:
            # set an 'auth' context to 'auth':
            context['auth'] = 'auth'
        # then, return the context.
        return context
    # Modifies the 'get' method as follows:
    def get(self, request, *args, **kwargs):
        # Attempts to retrieve the given page's object. If the 'try' is unsuccessful, the page's object does not currently exist.
        try:
            self.object = self.get_object()
            self.object.inchits()
        # If the Http404 exception is thrown, redirect to the edit page of the new page
        except Http404:
            return redirect('wiki:edit', pk=self.kwargs['pk'])
        # If the 'try' was successful, the context data is set to the page's object:
        context = self.get_context_data(object=self.object)
        # Then, this page's object is rendered into the page template
        return render(request, self.template_name, context)


class EditView(LoginRequiredMixin, generic.DetailView):
    '''Class-based view for editing pages'''

    login_url = reverse_lazy('wiki:login')
    # Retrieves the correct model
    model = Page
    # Points to the correct template
    template_name = 'wiki/edit.html'
    # Defines a context object name for reference in the 'edit' template
    context_object_name='page'
    # Modifies the 'post' method as follows:
    def post(self, request, *args, **kwargs):
        # Defines a variable containing the primary key of the page
        prim_key = self.kwargs['pk']
        # If the user got here via POSTing a save to the page:
        if 'Save' in request.POST:
            # Define a variable containing the tuple of retrieving the page object, or creating it if it does not exist:
            page, _ = Page.objects.get_or_create(page_name=prim_key)
            # Set the page content to the 'pagecontent' key value:
            page.page_content = request.POST['pagecontent']
            # Save the page changes:
            page.save()
            # Redirect to the given page, using its primary key
            return redirect('wiki:pageview', pk=prim_key)
        # Else, if the user did not get here via POSTing a save to the page, try retrieving the page's object and redirect to it
        else:
            try:
                page = Page.objects.get(pk=prim_key)
                return redirect('wiki:pageview', pk=prim_key)
            # If the DoesNotExist exception is thrown, redirect to the index
            except Page.DoesNotExist:
                return redirect('wiki:index')
    #Modifies the 'get' method as follows:
    def get(self, request, *args, **kwargs):
        # Defines a variable containing the primary key of the page
        prim_key = self.kwargs['pk']
        # Try retrieving the page's object
        try:
            page = Page.objects.get(page_name=prim_key)
        # If the DoesNotExist exception is thrown, the page []
        except Page.DoesNotExist:
            page = Page(prim_key)
        # Render the edit view with the page content
        return render(request, 'wiki/edit.html', {'page': page})

    # Modifies the 'get_context_data' method as follows:
    def get_context_data(self, **kwargs):
        # Defines a variable containing all context data
        context = super().get_context_data(**kwargs)
        # If the user is authenticated,
        if self.request.user.is_authenticated:
            # set the context to []:
            context['auth'] = 'auth'
        # then, return the context.
        return context

def upload_file(request):
    '''Function for file upload functionality. Determines if a request has been POSTed
    and sends the provided data (i.e. the file) to the form.'''

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = FileUploadForm()
    context = {}
    context['form'] = form
    context['files'] = UserFile.objects.all().order_by('content')
    for f in context['files']:
        f.displayname = split(f.content.name)[1]

    return render(request, 'wiki/upload.html', context)

def delete_file(request, pk):
    '''Function that deletes files based on the primary key of the request.'''

    UserFile.objects.get(pk=pk).delete()
    return redirect('wiki:upload')