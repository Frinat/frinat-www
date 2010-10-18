import os
import time

from django.db import models
from cms.models import CMSPlugin


def sponsor_path(instance, filename):
    _, ext = filename.rsplit('.')
    ext = ext.lower()
    try:
        ext = {
            'jpeg': 'jpg',
        }[ext]
    except KeyError:
        pass
    
    id = int(time.time() * 1000 * 100)
    
    return os.path.join('assets', 'sponsors', 'sponsor-{0}.{1}'.format(id, ext))


class Sponsor(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    logo = models.ImageField(upload_to=sponsor_path)
    
    def __unicode__(self):
        return u'{self.title} - {self.url}'.format(**locals())
    
    def get_exit_url(self):
        return self.url


class SpecificSponsorsPlugin(CMSPlugin):
    widget_title = models.CharField(max_length=100, default='Nos sponsors')
    sponsors = models.ManyToManyField(Sponsor)


class RandomSponsorsPlugin(CMSPlugin):
    widget_title = models.CharField(max_length=100, default='Nos sponsors')
    count = models.PositiveSmallIntegerField(default=3)
    
    @property
    def sponsors(self):
        return Sponsor.objects.order_by('?')[0:self.count]