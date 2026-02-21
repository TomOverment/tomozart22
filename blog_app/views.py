from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from django.views.generic import ListView

from .models import Post, Comment, Artwork
from .forms import PostForm, UpdateForm, CommentForm, ContactForm
from store.models import Product


# =============================
# HOME / INDEX
# =============================

class PostList(ListView):
    model = Post
    template_name = "blog_app/index.html"
    context_object_name = "object_list"
    ordering = ["-created_on"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        for post in queryset:
            post.can_edit = (
                user.is_authenticated and
                (user == post.author or user.is_staff)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(is_active=True)[:9]
        return context


# =============================
# PROFILE
# =============================

def profile(request):
    if request.user.is_authenticated:
        drafts = Post.objects.filter(
            author=request.user,
            status=0
        ).order_by('-created_on')

        published = Post.objects.filter(
            author=request.user,
            status=1
        ).order_by('-created_on')

        return render(
            request,
            'blog_app/profile.html',
            {
                'drafts': drafts,
                'published': published
            }
        )

    return redirect('account_login')


# =============================
# ADD POST
# =============================

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
                form.instance.slug = f"{original_slug}-{counter}"
                counter += 1

        form.save()
        messages.success(self.request, "Post created successfully!")
        return redirect('blog:home')


# =============================
# POST DETAIL
# =============================

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

            messages.success(
                request,
                "Comment submitted and awaiting approval"
            )
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
            "form": comment_form,
        },
    )


# =============================
# UPDATE POST
# =============================

class UpdatePost(generic.UpdateView):
    model = Post
    form_class = UpdateForm
    template_name = "blog_app/editposts.html"
    success_url = reverse_lazy("blog:home")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post updated successfully!")
        return super().form_valid(form)


# =============================
# DELETE POST
# =============================

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        raise PermissionDenied

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('blog:home')

    return render(
        request,
        'blog_app/post_confirm_delete.html',
        {'post': post}
    )


# =============================
# ABOUT
# =============================

def about(request):
    return render(request, "blog_app/about.html")


# =============================
# GALLERY
# =============================

def gallery(request):
    artworks = Artwork.objects.all()
    return render(
        request,
        'blog_app/gallery.html',
        {'artworks': artworks}
    )


# =============================
# FULL GALLERY VIEW
# =============================

def gallery_full(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    return render(
        request,
        "blog_app/gallery_full.html",
        {"artwork": artwork}
    )


# =============================
# CONTACT
# =============================

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            full_message = (
                f"Message from: {name}\n"
                f"Email: {email}\n\n"
                f"{message}"
            )

            send_mail(
                subject=f"[Tomozart Contact] {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    settings.ADMIN_EMAIL
                ] if settings.ADMIN_EMAIL else [
                    settings.DEFAULT_FROM_EMAIL
                ],
                fail_silently=False,
            )

            messages.success(
                request,
                "Thanks — your message has been sent."
            )
            return redirect("blog:contact")

        messages.error(request, "Please fix the errors and try again.")

    else:
        form = ContactForm()

    return render(
        request,
        "blog_app/contact.html",
        {"form": form}
    )