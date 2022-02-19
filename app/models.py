from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from .validators import PhoneNumberValidator


def get_image_filename(instance, filename):
    slug = instance.project.slug
    return "project_images/%s/%s" % (slug, filename)



class Image(models.Model):
    # project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)    raise error because project is abstract
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                    # related_name='images',            # this is not work
                                     limit_choices_to={'model__in':(
                                     'Article',
                                     'Web',
                                     'Mobile',
                                     'Library')})
    object_id = models.PositiveIntegerField()
    project = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to=get_image_filename, verbose_name='Image')



class Project(models.Model): # add link
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    #CATEGORY_CHOICES = (
    #    ('article', 'Article'),
    #    ('mobile', 'Mobile'),
    #    ('web', 'Web'),
    #    ('library', 'Library'),
    #)
    title = models.CharField(max_length=250)
    #category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='web')
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    images = GenericRelation(Image)   #  naming images raise an error :
                                      # TypeError: Direct assignment to the reverse side of a related set is prohibited. Use +.set() instead.
                                      # because i had a field in my form named images

    class Meta:
        abstract = True
        ordering = ('-created',)

    def __str__(self):
        return self.title



class Article(Project):
    description = models.TextField()


class Web(Project):
    language = models.CharField(max_length=250)
    technologies = models.TextField()

class Mobile(Project):
    language = models.CharField(max_length=250)
    technologies = models.TextField()
class Library(Project):
    language = models.CharField(max_length=250)
    technologies = models.TextField()

    class Meta:
        verbose_name = 'Library'
        verbose_name_plural = 'Libraries'




class Skill(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    level = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        ordering = ['name']


    def __str__(self):
        return self.name





class ContactMessage(models.Model):
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255)
    sender_mail = models.EmailField(_('Email Address'),
                            error_messages={
                                'unique': _("A user with that email already exists."),
                            },
                            blank=True,)
    phone_validator = PhoneNumberValidator()
    sender_phone = models.CharField(_('Phone Number'), validators=[phone_validator], max_length=16,
                            blank=True,)

    class Meta:
        ordering = ('-sent_at',)


    def __str__(self):
        return f'sent at {self.sent_at}'

   # if you want to show errors to user, so you should write this code in clean() nor save()
    def clean(self):
        if not (self.sender_mail or self.sender_phone):
            # raise ValidationError("Both email and phone number can not be blank")              # this is showed in above and global
            raise ValidationError({
                'sender_phone': ValidationError(_('Both this field and phone number can not be blank.please fill one of them'), code='required_together_phone'),
                'sender_mail': ValidationError(_('Both this field and email can not be blank.please fill one of them.'), code='required_together_phone'),
            })
        super().clean()
