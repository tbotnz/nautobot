from nautobot.core.apps import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuImportButton, NavMenuTab


menu_items = (
    NavMenuTab(
        name="Organization",
        weight=100,
        groups=(
            NavMenuGroup(
                name="Tags",
                weight=400,
                items=(
                    NavMenuItem(
                        link="extras:tag_list",
                        name="Tags",
                        weight=100,
                        permissions=[
                            "extras.view_tag",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:tag_add",
                                permissions=[
                                    "extras.add_tag",
                                ],
                            ),
                            NavMenuImportButton(
                                link="extras:tag_import",
                                permissions=[
                                    "extras.add_tag",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Statuses",
                weight=500,
                items=(
                    NavMenuItem(
                        link="extras:status_list",
                        name="Statuses",
                        weight=100,
                        permissions=[
                            "extras.view_status",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:status_add",
                                permissions=[
                                    "extras.add_status",
                                ],
                            ),
                            NavMenuImportButton(
                                link="extras:status_import",
                                permissions=[
                                    "extras.add_status",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Dynamic Groups",
                weight=500,
                items=(
                    NavMenuItem(
                        link="extras:dynamicgroup_list",
                        name="Dynamic Groups",
                        weight=100,
                        permissions=[
                            "extras.view_dynamicgroup",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:dynamicgroup_add",
                                permissions=[
                                    "extras.add_dynamicgroup",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Secrets",
        weight=700,
        groups=(
            NavMenuGroup(
                name="Secrets",
                weight=100,
                items=(
                    NavMenuItem(
                        link="extras:secret_list",
                        name="Secrets",
                        weight=100,
                        permissions=["extras.view_secret"],
                        buttons=(
                            NavMenuAddButton(link="extras:secret_add", permissions=["extras.add_secret"]),
                            NavMenuImportButton(link="extras:secret_import", permissions=["extras.add_secret"]),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:secretsgroup_list",
                        name="Secret Groups",
                        weight=200,
                        permissions=["extras.view_secretsgroup"],
                        buttons=(
                            NavMenuAddButton(link="extras:secretsgroup_add", permissions=["extras.add_secretsgroup"]),
                        ),
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Jobs",
        weight=800,
        groups=(
            NavMenuGroup(
                name="Jobs",
                weight=100,
                items=(
                    NavMenuItem(
                        link="extras:job_list",
                        name="Jobs",
                        weight=100,
                        permissions=[
                            "extras.view_job",
                        ],
                        buttons=(),
                    ),
                    NavMenuItem(
                        link="extras:scheduledjob_approval_queue_list",
                        name="Job Approval Queue",
                        weight=200,
                        permissions=[
                            "extras.view_job",
                        ],
                        buttons=(),
                    ),
                    NavMenuItem(
                        link="extras:scheduledjob_list",
                        name="Scheduled Jobs",
                        weight=300,
                        permissions=[
                            "extras.view_job",
                            "extras.view_scheduledjob",
                        ],
                        buttons=(),
                    ),
                    NavMenuItem(
                        link="extras:jobresult_list",
                        name="Job Results",
                        weight=400,
                        permissions=[
                            "extras.view_jobresult",
                        ],
                        buttons=(),
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Extensibility",
        weight=900,
        groups=(
            NavMenuGroup(
                name="Logging",
                weight=100,
                items=(
                    NavMenuItem(
                        link="extras:objectchange_list",
                        name="Change Log",
                        weight=100,
                        permissions=[
                            "extras.view_objectchange",
                        ],
                        buttons=(),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Data Sources",
                weight=200,
                items=(
                    NavMenuItem(
                        link="extras:gitrepository_list",
                        name="Git Repositories",
                        weight=100,
                        permissions=[
                            "extras.view_gitrepository",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:gitrepository_add",
                                permissions=[
                                    "extras.add_gitrepository",
                                ],
                            ),
                            NavMenuImportButton(
                                link="extras:gitrepository_import",
                                permissions=[
                                    "extras.add_gitrepository",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Data Management",
                weight=300,
                items=(
                    NavMenuItem(
                        link="extras:graphqlquery_list",
                        name="GraphQL Queries",
                        weight=100,
                        permissions=[
                            "extras.view_graphqlquery",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:graphqlquery_add",
                                permissions=[
                                    "extras.add_graphqlquery",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:relationship_list",
                        name="Relationships",
                        weight=200,
                        permissions=[
                            "extras.view_relationship",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:relationship_add",
                                permissions=[
                                    "extras.add_relationship",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Automation",
                weight=500,
                items=(
                    NavMenuItem(
                        link="extras:configcontext_list",
                        name="Config Contexts",
                        weight=100,
                        permissions=[
                            "extras.view_configcontext",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:configcontext_add",
                                permissions=[
                                    "extras.add_configcontext",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:configcontextschema_list",
                        name="Config Context Schemas",
                        weight=100,
                        permissions=[
                            "extras.view_configcontextschema",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:configcontextschema_add",
                                permissions=[
                                    "extras.add_configcontextschema",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:exporttemplate_list",
                        name="Export Templates",
                        weight=200,
                        permissions=[
                            "extras.view_exporttemplate",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:exporttemplate_add",
                                permissions=[
                                    "extras.add_exporttemplate",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:webhook_list",
                        name="Webhooks",
                        weight=400,
                        permissions=[
                            "extras.view_webhook",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:webhook_add",
                                permissions=[
                                    "extras.add_webhook",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Miscellaneous",
                weight=600,
                items=(
                    NavMenuItem(
                        link="extras:computedfield_list",
                        name="Computed Fields",
                        weight=100,
                        permissions=[
                            "extras.view_computedfield",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:computedfield_add",
                                permissions=[
                                    "extras.add_computedfield",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:customfield_list",
                        name="Custom Fields",
                        weight=200,
                        permissions=[
                            "extras.view_customfield",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:customfield_add",
                                permissions=[
                                    "extras.add_customfield",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:customlink_list",
                        name="Custom Links",
                        weight=300,
                        permissions=[
                            "extras.view_customlink",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:customlink_add",
                                permissions=[
                                    "extras.add_customlink",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Plugins",
        weight=5000,
        groups=(
            NavMenuGroup(
                name="General",
                weight=100,
                items=(
                    NavMenuItem(
                        link="plugins:plugins_list",
                        name="Installed Plugins",
                        weight=100,
                        permissions=[],
                        buttons=(),
                    ),
                ),
            ),
        ),
    ),
)
