from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Post, Comment
from cloudinary.uploader import upload
from .forms import PostForm, UpdateForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden
from .models import Artwork
from django.utils.text import slugify
from django.urls import reverse_lazy



class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = "blog_app/index.html"
    paginate_by = 6


def profile(request):
    if request.user.is_authenticated:
        drafts = Post.objects.filter(author=request.user,
                                     status=0).order_by('-created_on')
        published = Post.objects.filter(author=request.user,
                                        status=1).order_by('-created_on')
        return render(request, 'blog_app/profile.html',
                      {'drafts': drafts, 'published': published})
    else:
        return redirect('login')


def about(request):
    return render(request, 'blog_app/about.html')


class AddPostView(generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog_app/addpost.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
            original_slug = form.instance.slug
            counter = 1
            while Post.objects.filter(slug=form.instance.slug).exists():
                form.instance.slug = f'{original_slug}-{counter}'
                counter += 1
        form.save()
        messages.add_message(self.request, messages.SUCCESS,
                             'Post created successfully!')
        return redirect('home')


def post_detail(request, slug):
    queryset = Post.objects.filter(status=1)
    post = get_object_or_404(queryset, slug=slug)
    comments = post.comments.all().order_by("-created_on")
    comment_count = post.comments.filter(approved=True).count()
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Comment submitted and awaiting approval')
            return HttpResponseRedirect(request.path_info)
    else:
        comment_form = CommentForm()
    return render(
        request,
        "blog_app/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_count": comment_count,
            "form": comment_form
        }
    )


class PostDetail(generic.DetailView):
    model = Post
    template_name = "blog_app/post_detail.html"



class UpdatePost(generic.UpdateView):
    model = Post
    form_class = UpdateForm
    template_name = "blog_app/editposts.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Post updated successfully!')
        return super().form_valid(form)


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        raise PermissionDenied
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return render(request, 'blog_app/post_confirm_delete.html', {'post': post})



def gallery(request):
    artworks = Artwork.objects.all()
    return render(request, 'gallery.html', {'artworks': artworks})


def register(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Registration successful. You can now log in.')
            return redirect('account_login')
    else:
        form = CustomSignupForm()
    return render(request, 'registration/signup.html', {'form': form})
