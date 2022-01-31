"""Dynamic Groups Models."""

import logging
import uuid

from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction

from nautobot.extras.models import ChangeLoggedModel
from nautobot.core.models import BaseModel
from nautobot.utilities.utils import get_filterset_for_model, get_dynamicgroupmap_for_model
from nautobot.utilities.querysets import RestrictedQuerySet


class DynamicGroupQuerySet(RestrictedQuerySet):
    """Queryset for `DynamicGroup` objects."""

    def get_for_object(self, obj):
        """
        Return all `DynamicGroup` assigned to the given object.
        """
        if not isinstance(obj, models.Model):
            raise TypeError(f"{obj} is not an instance of Django Model class")

        # Check if dynamicgroup is supported for this model
        model = obj._meta.model
        dynamicgroupmap = get_dynamicgroupmap_for_model(model)

        if not dynamicgroupmap:
            return self

        dynamicgroup_filter = dynamicgroupmap.get_queryset_filter(obj)
        return self.filter(content_type=ContentType.objects.get_for_model(obj)).filter(dynamicgroup_filter)


class DynamicGroup(BaseModel, ChangeLoggedModel):
    """Dynamic Group Model."""

    name = models.CharField(max_length=100, unique=True, help_text="Internal Dynamic Group name")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)

    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        verbose_name="Object Type",
        help_text="The type of object for this group.",
    )
    _members_cache = models.JSONField(
        encoder=DjangoJSONEncoder,
        blank=True,
        editable=False,
        default=list,
    )
    _members_count = models.PositiveIntegerField(editable=False, blank=True, default=0)

    filter = models.JSONField(
        encoder=DjangoJSONEncoder,
        blank=True,
        null=True,
        help_text="",
    )

    objects = DynamicGroupQuerySet.as_manager()

    def __str__(self):
        """Group Model string return."""
        return self.name.capitalize()

    # def clean(self):
    #     """Group Model clean method."""
    #     model = self.content_type.model_class()

    #     if self.filter:
    #         try:
    #             filterset_class = get_filterset_for_model(model)
    #         except AttributeError:
    #             raise ValidationError(  # pylint: disable=raise-missing-from
    #                 {"filter": "Unable to find a FilterSet for this model."}
    #             )

    #         filterset = filterset_class(self.filter, model.objects.all())

    #         if filterset.errors:
    #             for key in filterset.errors:
    #                 raise ValidationError({"filter": f"{key}: {filterset.errors[key]}"})

    def get_queryset(self):
        """Define custom queryset for group model."""

        model = self.content_type.model_class()

        if not self.filter:
            return model.objects.none()

        dynamicgroupmap_class = get_dynamicgroupmap_for_model(model)
        return dynamicgroupmap_class.get_queryset(self.filter)

    @property
    def count(self):
        """Return the number of objects in the group."""
        # return self.get_queryset().count()
        return self._members_count

    def get_dynamicgroup_url(self):
        """Get url to group members."""
        model = self.content_type.model_class()
        # Move this function to dgm class to simplify support for plugin
        base_url = reverse(f"{model._meta.app_label}:{model._meta.model_name}_list")

        dynamicgroupmap_class = get_dynamicgroupmap_for_model(model)

        filter_str = dynamicgroupmap_class.get_filterset_as_string(self.filter)

        # FIXME(jathan): This seems incredibly fragile.
        if filter_str:
            return f"{base_url}?{filter_str}"

        return base_url

    @property
    def map(self):
        if getattr(self, "_map", None) is None:
            model = self.content_type.model_class()
            dynamicgroupmap_class = get_dynamicgroupmap_for_model(model)
            self._map = dynamicgroupmap_class

        return self._map

    def _purge_assignments(self):
        self.dg_assignments.all().delete()
        self.clean_assignments()

    def clean_assignments(self):
        member_pks = self.dg_assignments.values_list("object_id", flat=True)
        # self._members_cache = json.dumps(assignments, cls=DjangoJSONEncoder)
        self._members_cache = [str(m) for m in member_pks]
        self.clean_count()

    def clean_count(self):
        count = self.dg_assignments.count()
        self._members_count = count

    def _assign_member(self, member):
        """Assign an object to this DynamicGroup."""
        dga = DynamicGroupAssignment(
            dynamic_group=self,
            content_object=member,
        )
        dga.full_clean()
        return dga

    @transaction.atomic
    def assign_members(self, members):
        """Assign a list of members to this DynamicGroup."""
        # First purge existing assignments.
        self._purge_assignments()

        # Then create the new ones.
        new_members = []
        for member in members:
            new_members.append(self._assign_member(member))

        # Assert that assignments are cached and the count is updated.
        # self.clean_assignments()

        return new_members

    def save(self, **kwargs):
        members = self.get_queryset()
        new_members = self.assign_members(members)
        DynamicGroupAssignment.objects.bulk_create(new_members)
        self.clean_assignments()  # Cache new assignments
        super().save(**kwargs)


class DynamicGroupAssignment(ChangeLoggedModel, BaseModel):
    """Intermediate model for assignment of objects to DynamicGroups."""

    dynamic_group = models.ForeignKey(
        "extras.DynamicGroup", 
        related_name="dg_assignments",
        on_delete=models.CASCADE,
        db_index=True,
        help_text="Dynamic Group to which this assignment is bound."
    )
    content_type = models.ForeignKey(
        ContentType,
        related_name="dg_assignments",
        on_delete=models.CASCADE,
        db_index=True,
    )
    object_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    def clean(self):
        if self.content_type != self.dynamic_group.content_type:
            raise ValidationError({
                "content_type": "Object content_type must match that of the DynamicGroup to which it is assigned"
            })

    def __str__(self):
        return f"{self.content_object!r} -> {self.dynamic_group!r}"


from django.dispatch import receiver
from django.db.models import signals

logger = logging.getLogger(__name__)

skip_models = ["dynamicgroupassignment"]


@receiver(signals.pre_save)
def stash_existing_dynamic_group_memberships(sender, instance, raw=False, **kwargs):
    # Only make changes if this isn't raw (e.g. during fixture loading)
    if raw:
        return

    # Only work w/ objects that inherit from BaseModel
    model_name = sender._meta.model_name
    if not issubclass(sender, BaseModel) or model_name in skip_models:
        return

    skip = ["example_plugin"]
    if instance._meta.app_label in skip:
        return

    if hasattr(instance, "dynamic_groups"):
        logger.debug("Instance %r about to be saved/deleted; stashing Dynamic Groups", instance)
        instance._existing_dynamic_groups = list(
            instance.dynamic_groups.all()
            # instance.dynamic_groups.select_related("dynamic_group")
        )


@receiver(signals.post_save)
@receiver(signals.post_delete)
def refresh_dynamic_group_membership(sender, instance, created=False, raw=False, **kwargs):
    # Only make changes if this isn't raw (e.g. during fixture loading)
    if raw:
        return

    # Only work w/ objects that inherit from BaseModel
    model_name = sender._meta.model_name
    if not issubclass(sender, BaseModel) or model_name in skip_models:
        return

    logger.debug("Instance %r saved/deleted", instance)

    # Enumerate the NEW assignments for the instance and call `save()` on each
    # DynamicGroup
    groups_to_update = set()
    if hasattr(instance, "dynamic_groups"):
        for dga in instance.dynamic_groups.select_related("dynamic_group"):
            logger.debug("Refreshing NEW dynamic group %r", dga)
            groups_to_update.add(dga.dynamic_group)
            # dga.dynamic_group.save()

    # Enumerate the OLD assignments for the instance and call `save()` on each
    # DynamicGroup
    if hasattr(instance, "_existing_dynamic_groups"):
        for dga in instance._existing_dynamic_groups:
            logger.debug("Refreshing OLD dynamic group %r", dga)
            groups_to_update.add(dga.dynamic_group)
            # dga.dynamic_group.save()

    # Call `save()` on the ones we need to update
    for group in groups_to_update:
        group.save()

    # Find DynamicGroups for which this instance is now eligible, and update
    # them.
    from nautobot.utilities.utils import get_dynamicgroupmap_for_model
    map_class = get_dynamicgroupmap_for_model(instance._meta.model)
    if map_class is not None:
        new_filter = map_class.get_queryset_filter(instance)
        new_groups = DynamicGroup.objects.filter(new_filter)
        for new_group in new_groups:
            logger.debug("Refreshing NEW dynamic group %r", new_group)
            new_group.save()
