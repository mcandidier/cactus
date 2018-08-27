from django.db import models
from django.contrib import messages
from django import forms 
from django.shortcuts import render, redirect, get_object_or_404

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from wagtail.search import index
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager

from taggit.models import TaggedItemBase, Tag


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=250)
    icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    @property
    def blogs(self):
        return self.blogpage_set.live()
    
    class Meta: 
        verbose_name = 'blog category'
        verbose_name_plural = 'blog categories'


class BlogIndexPage(RoutablePageMixin, Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context

    # Returns the child BlogPage objects for this BlogPageIndex.
    # If a tag or category is used then it will filter the posts.
    def get_posts(self, **kwargs):
        posts = BlogPage.objects.live().descendant_of(self)
        tag = kwargs.get('tag', None)
        category = kwargs.get('category', None)

        if tag:
            posts = posts.filter(tags=tag)
        if category: 
            posts = posts.filter(category=category)
        return posts

    @route('^tags/$', name='tag_page')
    @route('^tags/([\w-]+)/$', name='tag_page')
    def tag_page(self, request, tag=None):
        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no blog posts tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)
        blogpages = self.get_posts(tag=tag)
        context = {
            'tag': tag,
            'blogpages': blogpages
        }
        return render(request, 'blog/blog_index_page.html', context)

    @route('^category/$', name='category_page')
    @route('^category/([\w-]+)/$', name='category_page')
    def category_page(self, request, category=None):
        context = {}
        try:
            category = BlogCategory.objects.get(name=category)
        except BlogCategory.DoesNotExist:
            context['categories'] = BlogCategory.objects.all()
            return render(request, 'blog/blog_categories.html', context)
        context['blogpages'] = self.get_posts(categories=category)
        return render(request, 'blog/blog_index_page.html', context)


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogPage', related_name='tagged_items',
        on_delete=models.CASCADE
    )

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),  
    ] 

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple)
        ], heading="blog information"),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label='Gallery images')
    ]

    def main_image(self):
        gallery_image = self.gallery_images.first()
        if gallery_image:
            return gallery_image.image
        return None

    @property
    def blog_page(self):
        return self.get_parent().specific
   
    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """
        tags = self.tags.all()
        for tag in tags:
            tag.url = '/'+'/'.join(s.strip('/') for s in [
                self.get_parent().url,
                'tags',
                tag.slug
            ])
        return tags

class BlogPageGalleryImages(Orderable):
    page = ParentalKey(BlogPage,
        on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey('wagtailimages.Image', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption')
    ]