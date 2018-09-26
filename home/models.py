from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.snippets.models import register_snippet


class HomePage(Page):
    """ Home page models
    """
    hero_title = models.CharField(max_length=1024)
    hero_body = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Hero image"
    )
    hero_cta_text = models.CharField(max_length=250, blank=True)
    hero_cta_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    #featured components
    feature_section_1 = models.CharField(max_length=520, help_text="Title for feature 1")
    featre_section_1_page = models.ForeignKey(
        'wagtailcore.Page',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Feature 1 to be displayed in homepage.',
        related_name='+'
    )

    #featured components
    feature_section_2 = models.CharField(max_length=520, help_text="Title for feature 1")
    featre_section_2_page = models.ForeignKey(
        'wagtailcore.Page',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Feature 1 to be displayed in homepage.',
        related_name='+'
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            ImageChooserPanel('hero_image', heading='hero main image'),
            FieldPanel('hero_title'),
            FieldPanel('hero_body', classname='full'),
            MultiFieldPanel([
                PageChooserPanel('hero_cta_link'),
                FieldPanel('hero_cta_text'),
            ])
        ]),
        MultiFieldPanel([
            FieldPanel('feature_section_1'),
            PageChooserPanel('featre_section_1_page')
        ], heading='Featured Section 1'),
        MultiFieldPanel([
            FieldPanel('feature_section_2'),
            PageChooserPanel('featre_section_2_page')
        ], heading='Featured Section 2')
    ]



class StandardPage(Page):
    """ Standard page models.
    """
    hero_title = models.CharField(max_length=1024)
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Hero image"
    ) 
    hero_text = models.CharField(max_length=1024)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel('hero_image'),
        MultiFieldPanel([
            FieldPanel('hero_title'),
            FieldPanel('hero_text')
        ]),
        FieldPanel('body', classname="full")
    ]


@register_snippet
class SocialItems(models.Model):
    """Social pages
    """
    name = models.CharField(max_length=128)
    link = models.URLField(blank=True, null=True, help_text='your social page url')
    icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('link'),
        ImageChooserPanel('icon')
    ]

    def __str__(self):
        return self.name