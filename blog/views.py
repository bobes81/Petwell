from cloudinary.exceptions import Error as CloudinaryError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BlogPostForm, NewsletterForm
from .models import BlogPost, Subscriber


def blog_list(request):
    posts = BlogPost.objects.all()
    return render(request, "blog/blog_list.html", {"posts": posts})


def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, "blog/blog_detail.html", {"post": post})


@login_required
def create_post(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            try:
                with transaction.atomic():
                    blog_post.save()
            except (CloudinaryError, ValueError):
                form.add_error(
                    "image",
                    "Image upload is unavailable. "
                    "Try again or submit without a new image.",
                )
            else:
                messages.success(request, "Your post was published.")
                return redirect("blog:blog_list")
    else:
        form = BlogPostForm()
    return render(request, "blog/blog_form.html", {"form": form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if post.author_id != request.user.pk and not request.user.is_staff:
        return HttpResponseForbidden(
            "Only the author or staff may change this post."
        )
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
            except (CloudinaryError, ValueError):
                form.add_error(
                    "image",
                    "Image upload is unavailable. "
                    "Your changes were not saved; please retry.",
                )
            else:
                messages.success(request, "Your post was updated.")
                return redirect("blog:blog_detail", pk=post.pk)
    else:
        form = BlogPostForm(instance=post)
    return render(request, "blog/blog_form.html", {"form": form, "edit": True})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if post.author_id != request.user.pk and not request.user.is_staff:
        return HttpResponseForbidden(
            "Only the author or staff may change this post."
        )
    if request.method == "POST":
        post.delete()
        messages.success(request, "Your post was deleted.")
        return redirect("blog:blog_list")
    return render(request, "blog/blog_confirm_delete.html", {"post": post})


@require_POST
def subscribe(request):
    form = NewsletterForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please enter a valid email address.")
        return redirect("home")

    _, created = Subscriber.objects.get_or_create(
        email=form.cleaned_data["email"]
    )
    if created:
        messages.success(
            request, "Thank you for subscribing to our newsletter!"
        )
    else:
        messages.info(request, "This email is already subscribed.")
    return redirect("home")
