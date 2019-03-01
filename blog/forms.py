from django import forms
from blog.models import Comment

class CommentForm(forms.ModelForm):
   class Meta:
     model = Comment
     fields = ('name','email','content')

   def add_comment(self):
       print("this func works")
