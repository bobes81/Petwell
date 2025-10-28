@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if request.user != post.author and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    try:
        if request.method == 'POST':
            form = BlogPostForm(request.POST, request.FILES, instance=post)

            if form.is_valid():
              
                if not request.FILES.get('image'):
                    post.title = form.cleaned_data['title']
                    post.content = form.cleaned_data['content']
                   
                    post.save(update_fields=['title', 'content'])
                else:
                    form.save()

                messages.success(request, 'Post updated successfully!')
                return redirect('blog:blog_list')

            else:
                messages.error(request, 'Please correct the errors below.')

        else:
           
            form = BlogPostForm(instance=post)

    except Exception as e:
        print(f"❌ Safe Edit Error: {e}")
        messages.error(request, f"An unexpected error occurred: {e}")
        return redirect('blog:blog_list')

    return render(request, 'blog/blog_form.html', {'form': form, 'post': post})