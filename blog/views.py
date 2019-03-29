import json
import urllib

import datetime


from django.contrib import messages


from django.shortcuts import render

from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView
from django.views.generic.detail import SingleObjectMixin


from SezinGumusBlog import settings
from blog.forms import CommentForm
from blog.models import Blog, Comment, Reference
from django.db.models import Q



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

    def form_valid(self,form):

        comment = form.save(commit=False)
        comment.created_date = datetime.datetime.now()
        comment.blog_id = self.id  # self.queryset.reverse()[0].blog.id




        ''' Begin reCAPTCHA validation '''
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        ''' End reCAPTCHA validation '''

        if result['success']:
            comment.save()
            messages.success(self.request, 'New comment added with success!')


        else:
            messages.error(self.request, 'Invalid reCAPTCHA. Please try again.')
            form = CommentForm()


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
