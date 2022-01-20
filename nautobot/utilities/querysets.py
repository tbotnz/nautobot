import logging

from django.db.models import Manager, Q
from django.db.models.fields.json import KeyTransform
from djangoql.queryset import DjangoQLQuerySet
import djangoql.schema as dql_schema

from nautobot.utilities.permissions import permission_is_exempt


log = logging.getLogger(__name__)


class CustomFieldSchema(dql_schema.DjangoQLSchema):
    # https://ishan1608.wordpress.com/2018/01/05/querying-jsonfield-in-django/
    def get_fields(self, model):
        from django.contrib.contenttypes.models import ContentType
        from nautobot.extras.models import CustomField
        from nautobot.extras.choices import CustomFieldFilterLogicChoices

        fields = super().get_fields(model)
        custom_fields = CustomField.objects.filter(content_types=ContentType.objects.get_for_model(model)).exclude(
            filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED
        )
        for cf in custom_fields:
            fields.append(dql_schema.StrField(name=f"cf_{cf.name}"))

        return fields


class RestrictedQuerySet(DjangoQLQuerySet):
    djangoql_schema = CustomFieldSchema

    def restrict(self, user, action="view"):
        """
        Filter the QuerySet to return only objects on which the specified user has been granted the specified
        permission.

        :param user: User instance
        :param action: The action which must be permitted (e.g. "view" for "dcim.view_site"); default is 'view'
        """
        # Resolve the full name of the required permission
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        permission_required = f"{app_label}.{action}_{model_name}"

        # Bypass restriction for superusers and exempt views
        if user.is_superuser or permission_is_exempt(permission_required):
            qs = self

        # User is anonymous or has not been granted the requisite permission
        elif not user.is_authenticated or permission_required not in user.get_all_permissions():
            qs = self.none()

        # Filter the queryset to include only objects with allowed attributes
        else:
            attrs = Q()
            for perm_attrs in user._object_perm_cache[permission_required]:
                if type(perm_attrs) is list:
                    for p in perm_attrs:
                        attrs |= Q(**p)
                elif perm_attrs:
                    attrs |= Q(**perm_attrs)
                else:
                    # Any permission with null constraints grants access to _all_ instances
                    attrs = Q()
                    break
            qs = self.filter(attrs)

        return qs


class RestrictedManager(Manager):
    queryset_class = RestrictedQuerySet

    def get_queryset(self):
        from django.contrib.contenttypes.models import ContentType
        from nautobot.extras.models import CustomField
        from nautobot.extras.choices import CustomFieldFilterLogicChoices

        qs = self.queryset_class(self.model, using=self._db)
        custom_fields = CustomField.objects.filter(content_types=ContentType.objects.get_for_model(self.model)).exclude(
            filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED
        )
        anno = {f"cf_{cf.name}": KeyTransform(cf.name, f"_custom_field_data__{cf.name}") for cf in custom_fields}

        return qs.annotate(**anno)
        # return qs

    def restrict(self, user, action="view"):
        return self.get_queryset().restrict(user, action=action)

    def djangoql(self, search, schema=None):
        return self.get_queryset().djangoql(search, schema=schema)
