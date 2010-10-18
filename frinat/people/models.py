import os
import time

from django.template.defaultfilters import slugify
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from cms.models import CMSPlugin

import mptt
try:
    from mptt.models import MPTTModel
except ImportError:
    MPTTModel = models.Model


def person_path(instance, filename):
    _, ext = filename.rsplit('.')
    ext = ext.lower()
    try:
        ext = {
            'jpeg': 'jpg',
        }[ext]
    except KeyError:
        pass

    id = int(time.time() * 1000 * 100)
    name = slugify(instance.full_name)
    return os.path.join('assets', 'people', '{0}-{1}.{2}'.format(name, id, ext))


class Group(MPTTModel):
    """Category object for Entry"""

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(help_text=_('used for publication'),
                            unique=True, max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True,
                               verbose_name=_('parent category'),
                               related_name='children')

    @property
    def tree_path(self):
        if self.parent:
            return u'%s/%s' % (self.parent.tree_path, self.slug)
        return u'%s' % self.slug

    def __unicode__(self):
        return self.tree_path

    class Meta:
        ordering = ['title']

    class MPTTMeta:
        order_insertion_by = ['title',]


class Person(models.Model):
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    groups = models.ManyToManyField(Group)
    user = models.ForeignKey(User, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    photo = models.ImageField(upload_to=person_path)
    
    def __unicode__(self):
        return self.full_name
        
    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('people')
    

class PeopleGroupPlugin(CMSPlugin):
    groups_to_display = models.ManyToManyField(Group)
    subgroups = models.BooleanField(default=False)


class SelectedPeoplePlugin(CMSPlugin):
    people_to_display = models.ManyToManyField(Person)


if hasattr(mptt, 'register'):
    mptt.register(Group, **dict([(attr, getattr(Group.MPTTMeta, attr))
                                    for attr in dir(Group.MPTTMeta)
                                    if attr[:1] != '_']))