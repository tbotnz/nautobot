import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.forms.models import model_to_dict

from nautobot.utilities.querysets import RestrictedQuerySet


class ModelDiffMixin:
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super().save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])


class BaseModel(models.Model, ModelDiffMixin):
    """
    Base model class that all models should inhert from.

    This abstract base provides globally common fields and functionality.

    Here we define the primary key to be a UUID field and set its default to
    automatically generate a random UUID value. Note however, this does not
    operate in the same way as a traditional auto incrementing field for which
    the value is issued by the database upon initial insert. In the case of
    the UUID field, Django creates the value upon object instantiation. This
    means the canonical pattern in Django of checking `self.pk is None` to tell
    if an object has been created in the actual database does not work because
    the object will always have the value populated prior to being saved to the
    database for the first time. An alternate pattern of checking `not self.present_in_database`
    can be used for the same purpose in most cases.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    dynamic_groups = GenericRelation("extras.DynamicGroupAssignment", related_query_name="dynamic_groups")
    '''
    dynamic_groups = GenericRelation(
        "extras.DynamicGroupAssignment",
        related_query_name="dynamic_groups_%(app_label)s_%(class)s",
    )
    dynamic_groups = models.ManyToManyField(
        "extras.DynamicGroup",
        db_index=True,
        related_name="%(app_label)s_%(class)s_related",
        through="extras.DynamicGroupAssignment",
        # through_fields=("dynamic_group", "content_type"),
        through_fields=("content_type", "dynamic_group"),
        help_text="Dynamic Groups to which this objects is assigned."
    )
    '''

    objects = RestrictedQuerySet.as_manager()

    @property
    def present_in_database(self):
        """
        True if the record exists in the database, False if it does not.
        """
        return not self._state.adding

    class Meta:
        abstract = True

    def validated_save(self):
        """
        Perform model validation during instance save.

        This is a convenience method that first calls `self.full_clean()` and then `self.save()`
        which in effect enforces model validation prior to saving the instance, without having
        to manually make these calls seperately. This is a slight departure from Django norms,
        but is intended to offer an optional, simplified interface for performing this common
        workflow. The indended use is for user defined Jobs and scripts run via the `nbshell`
        command.
        """
        self.full_clean()
        self.save()
