from datetime import timezone
import datetime
from functools import reduce

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template.backends import django
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, DetailView, CreateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin
from simple_search import SearchForm

from blog.forms import CommentForm
from blog.models import Blog, Comment, Reference
from django.db.models import Q
import operator


def blog_listview(request):
    template_name = 'html/blog_list.html'
    queryset = Blog.objects.all()
    context = {
        "blog_list": queryset
    }
    return render(request, template_name, context)


def blog_search_list_view(request):
    blogs = Blog.objects.all()
    query = request.GET.get('q')
    template_name = "html/results.html"

    if query:
        blogs = blogs.filter(Q(text__icontains=query) | Q(title__icontains=query) | Q(author__icontains=query))
    else:
        template_name = "html/blog_list.html"

    context = {"blog_list": blogs, "q": query}
    return render(request, template_name, context)


class BlogDisplay(DetailView):
    model = Blog
    template_name = 'html/blog_detail.html'
    queryset = Blog.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # super(BlogDisplay, self).get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context


class CommentView(SingleObjectMixin, FormView):

    form_class = CommentForm
    model = Comment
    template_name = 'html/blog_detail.html'
    queryset = Comment.objects.all()


    def get_blog_id (self,slug):
        blog = Blog.objects.get(slug=slug)
        print(blog)
        id = blog.id
        return id

    def get_queryset(self):
        blog = Blog.objects.get(slug=self.kwargs['slug'])
        comments = Comment.objects.filter(blog=blog)
        return comments

    def post(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()
        self.id       = self.get_blog_id(self.kwargs['slug'])
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.created_date = datetime.datetime.now()
        comment.blog_id = self.id  #self.queryset.reverse()[0].blog.id
        comment.save()
        return super(CommentView, self).form_valid(form)

    def get_success_url(self):
        slug = self.queryset.reverse()[0].blog.slug
        return reverse('blog_detail', kwargs={'slug': slug})


class BlogDetailView(View):

    def get(self, request, *args, **kwargs):
        view = BlogDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentView.as_view()
        return view(request, *args, **kwargs)


'''
    def get_object(self, queryset=None):
        slug = self.kwargs['slug']
        b_obj = Blog.objects.get(slug=slug)
        try:
            c_obj = Comment.objects.get(blog=b_obj)
        except Comment.DoesNotExist:
            c_obj = None
        return c_obj.blog.slug
'''
