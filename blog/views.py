@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if request.user != post.author and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)

         
            if 'image' not in request.FILES or not request.FILES['image']:
                # Zruší Cloudinary validaci a nechá původní URL beze změny
                updated_post.image = post.image

            updated_post.author = post.author

            try:
                updated_post.save(force_update=True)
                messages.success(request, 'Post updated successfully!')
            except Exception as e:
                # Pokud Cloudinary spadne, jen přeskakuje upload
                print(f"⚠️ Cloudinary edit error handled safely: {e}")
                updated_post.image = post.image
                updated_post.save(force_update=True)
                messages.success(request, 'Post updated without image update (Cloudinary skipped).')

            return redirect('blog:blog_list')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/blog_form.html', {'form': form, 'post': post})