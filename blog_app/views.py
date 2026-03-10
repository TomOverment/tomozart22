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

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import MailingListSignupForm
from .models import MailingListSubscriber


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

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        next_page = self.request.POST.get("next") or self.request.GET.get("next")

        if next_page == "profile":
            return reverse_lazy("blog:profile")

        if next_page == "home":
            return reverse_lazy("blog:home")

        return reverse_lazy("blog:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_page"] = self.request.GET.get("next", "home")
        return context

# =============================
# DELETE POST
# =============================

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        raise PermissionDenied

    next_page = request.POST.get("next") or request.GET.get("next", "home")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully!")

        if next_page == "profile":
            return redirect("blog:profile")
        return redirect("blog:home")

    return render(
        request,
        'blog_app/post_confirm_delete.html',
        {
            'post': post,
            'next_page': next_page,
        }
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
# ARTWORK DETAIL
# =============================

def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    return render(request, "blog_app/artwork_detail.html", {
        "artwork": artwork
    })
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

def bio(request):
    return render(request, "blog_app/bio.html")

# =============================
# MAILING LIST
# =============================

def newsletter(request):
    return render(request, "blog_app/newsletter.html")

@require_POST
def mailing_list_signup(request):
    form = MailingListSignupForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please enter a valid email.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    email = form.cleaned_data["email"].lower().strip()
    first_name = (form.cleaned_data.get("first_name") or "").strip()
    source = (form.cleaned_data.get("source") or "").strip()

    sub, created = MailingListSubscriber.objects.get_or_create(
        email=email,
        defaults={"first_name": first_name, "source": source, "is_active": True},
    )

    # If already exists, update name/source if newly provided
    changed = False
    if first_name and sub.first_name != first_name:
        sub.first_name = first_name
        changed = True
    if source and sub.source != source:
        sub.source = source
        changed = True
    if not sub.is_active:
        sub.is_active = True
        changed = True
    if changed:
        sub.save()

    # ---- Email YOU (notification) ----
    notify_to = getattr(settings, "NEWSLETTER_NOTIFY_EMAIL", None) or getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if notify_to:
        subject = f"New newsletter signup: {email}"
        text_body = render_to_string("emails/newsletter_notify.txt", {
            "email": email,
            "first_name": first_name,
            "source": source,
            "created": created,
        })
        EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[notify_to],
        ).send(fail_silently=True)

    # ---- Email CUSTOMER (welcome/success) ----
    customer_subject = render_to_string("emails/newsletter_welcome_subject.txt", {
        "first_name": first_name,
    }).strip()

    customer_text = render_to_string("emails/newsletter_welcome.txt", {
        "first_name": first_name,
        "email": email,
    })
    customer_html = render_to_string("emails/newsletter_welcome.html", {
        "first_name": first_name,
        "email": email,
    })

    msg = EmailMultiAlternatives(
        subject=customer_subject or "You're subscribed",
        body=customer_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    msg.attach_alternative(customer_html, "text/html")
    msg.send(fail_silently=True)

    messages.success(request, "You're subscribed! Please check your email.")
    return redirect(request.META.get("HTTP_REFERER", "/"))