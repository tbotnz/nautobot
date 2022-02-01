from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.urls import reverse
from rest_framework import status

from nautobot.dcim.models import Site
from nautobot.ipam.models import Prefix
from nautobot.extras.models import DynamicGroup, DynamicGroupAssociation
from nautobot.virtualization.models import VirtualMachine


class DynamicGroupTest(TestCase):
    def setUp(self):
        site_status = Status.objects.get_for_model(Site).get(slug="active")
        prefix_status = Status.objects.get_for_model(Prefix).get(slug="active")
        site_a = Site.objects.create(name="Site A", slug="site-a", status=site_status)
        site_b = Site.objects.create(name="Site B", slug="site-b", status=site_status)
        prefix1 = Prefix.objects.create(prefix="192.168.0.0/24", site=site_a, status=prefix_status)
        prefix2 = Prefix.objects.create(prefix="192.168.1.0/24", site=site_b, status=prefix_status)

        # dg1 = DynamicGroup.objects.
