# Create your views here.

from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.http.response import Http404
from .models import Page
from django.contrib.auth import views as auth_views, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

def register_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(username=username, password=password)
            user.save()
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('wiki:index')
    else:
        form = UserCreationForm()
    return render(request, 'wiki/create_user.html', {'form': form})

class WikiLoginView(auth_views.LoginView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['auth'] = 'auth'
        return context

    template_name = 'wiki/login.html'

class WikiLogoutView(auth_views.LogoutView):
    def get_next_page(self):
        return reverse('wiki:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['auth'] = 'auth'
        return context

class IndexView(generic.ListView):
    template_name = 'wiki/index.html'
    context_object_name = 'pages'

    def get_queryset(self):
        return Page.objects.all().order_by('page_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['auth'] = 'auth'
        return context

class PageView(generic.DetailView):
    model = Page
    template_name = 'wiki/page.html'
    context_object_name = 'this_page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['auth'] = 'auth'
        return context

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return redirect('wiki:edit', pk=self.kwargs['pk'])
        context = self.get_context_data(object=self.object)
        return render(request, self.template_name, context)

class EditView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('wiki:login')
    model = Page
    template_name = 'wiki/edit.html'
    context_object_name='page'

    def post(self, request, *args, **kwargs):
        PrimKey = self.kwargs['pk']
        
        if 'Save' in request.POST:
            page, created = Page.objects.get_or_create(page_name=PrimKey)
            page.page_content = request.POST['pagecontent']
            page.save()
            return redirect('wiki:pageview', pk=PrimKey)
        else:
            try:
                page = Page.objects.get(pk=PrimKey)
                return redirect('wiki:pageview', pk=PrimKey)
            except Page.DoesNotExist:
                return redirect('wiki:index')
        
    def get(self, request, *args, **kwargs):
        PrimKey = self.kwargs['pk']
        try:
            page = Page.objects.get(page_name=PrimKey)
        except Page.DoesNotExist:
            page = Page(PrimKey)
        return render(request, 'wiki/edit.html', {'page': page})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['auth'] = 'auth'
        return context