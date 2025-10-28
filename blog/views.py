from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import BlogPost
from .forms import BlogPostForm


def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts, 'user': request.user})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'New blog post created successfully!')
            return redirect('blog:blog_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm()
    return render(request, 'blog/blog_form.html', {'form': form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user != post.author and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this post.")
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('blog:blog_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog/blog_form.html', {'form': form, 'post': post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    # 🔒 Allow only author or admin to delete
    if request.user != post.author and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == 'POST':
        # 🧹 Try to delete associated image safely
        if hasattr(post, 'image') and post.image:
            try:
                image_field = getattr(post, 'image')
                if hasattr(image_field, 'delete'):
                    image_field.delete(save=False)
            except Exception as e:
                print(f"⚠️ Error deleting image from Cloudinary: {e}")

        # 🗑️ Delete the blog post safely
        try:
            post.delete()
            messages.success(request, 'Post deleted successfully!')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred while deleting the post: {e}")

        return redirect('blog:blog_list')

    return render(request, 'blog/blog_confirm_delete.html', {'post': post})


def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog/blog_detail.html', {'post': post, 'user': request.user})