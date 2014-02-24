from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from frinat.sponsors import models
from django.utils.translation import ugettext_lazy as _


class CMSSpecificSponsorPlugin(CMSPluginBase):
    module = _('sponsors')
    model = models.SpecificSponsorsPlugin
    name = _("Specific sponsors sidebar widget")
    render_template = "sponsors/list.html"

    def render(self, context, instance, placeholder):
        context.update({
            'title': instance.widget_title,
            'sponsors': instance.sponsors.all(),
        })

        return context

plugin_pool.register_plugin(CMSSpecificSponsorPlugin)


class CMSRandomSponsorPlugin(CMSSpecificSponsorPlugin):
    model = models.RandomSponsorsPlugin
    name = _("Random sponsors sidebar widget")

plugin_pool.register_plugin(CMSRandomSponsorPlugin)
