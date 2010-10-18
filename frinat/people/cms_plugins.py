import datetime
import itertools

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from frinat.people import models
from django.utils.translation import ugettext_lazy as _


class CMSPeopleGroupPlugin(CMSPluginBase):
    module = _('people')
    model = models.PeopleGroupPlugin
    name = _("Group member listing")
    render_template = "people/list.html"
    
    def render(self, context, instance, placeholder):
        people = models.Person.objects.all()

        groups = instance.groups_to_display.all()
        
        print groups
        print dir(groups[0])
        
        if instance.subgroups:
            groups = itertools.chain(groups, *[g.get_descendants() for g in groups])
        
        context.update({
            'people': people,
        })
        
        return context

plugin_pool.register_plugin(CMSPeopleGroupPlugin)


class CMSSelectedPeoplePlugin(CMSPeopleGroupPlugin):
    model = models.SelectedPeoplePlugin
    name = _("Selected member listing")
    
    def render(self, context, instance, placeholder):
        context.update({
            'people': instance.people_to_display.all(),
        })
        
        return context

plugin_pool.register_plugin(CMSSelectedPeoplePlugin)