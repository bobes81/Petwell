from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsletterForm
from .models import BlogPost

def blog_list(request):
    posts = BlogPost.objects.all()
    return render(request, 'blog/blog_list.html', {'posts': posts})

def subscribe(request):
    """Handles newsletter subscription form."""
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for subscribing to our newsletter!")
            return redirect("home")
    else:
        form = NewsletterForm()
    return render(request, "newsletter.html", {"form": form})
