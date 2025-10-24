from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import BlogPost
from .forms import BlogPostForm


def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})


@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # uloží aktuálního přihlášeného uživatele
            post.save()
            return redirect('blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'blog/blog_form.html', {'form': form})


@login_required
def blog_update(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    form = BlogPostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog_list')
    return render(request, 'blog/blog_form.html', {'form': form})


@login_required
def blog_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('blog_list')
    return render(request, 'blog/blog_confirm_delete.html', {'post': post})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import BlogPostForm
from .models import BlogPost

@login_required
def create_post(request):
    """Create a new blog post"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been created successfully!')
            return redirect('blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Add New Post'})

@login_required
def edit_post(request, pk):
    """Edit an existing post"""
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user != post.author:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('blog_list')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been updated!')
            return redirect('blog_list')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post'})

@login_required
def delete_post(request, pk):
    """Delete a post"""
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user != post.author:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('blog_list')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been deleted.')
        return redirect('blog_list')

    return render(request, 'blog/confirm_delete.html', {'post': post})
