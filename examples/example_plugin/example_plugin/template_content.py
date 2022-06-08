from django.urls import reverse

from nautobot.extras.plugins import PluginTemplateExtension


class CircuitContent(PluginTemplateExtension):
    model = "circuits.circuit"

    def object_detail_tabs(self):
        return {
            "pct": {
                "title": "Example Plugin Circuit Tab",
                "url": reverse("plugins:example_plugin:circuit_detail_tab", args=[self.context["object"].pk]),
            },
        }


class DeviceContent(PluginTemplateExtension):
    model = "dcim.device"

    def object_detail_tabs(self):
        # You can define extra object detail page tabs within this file by
        return {
            "pdt": {
                "title": "Example Plugin Device Tab",
                "url": reverse("plugins:example_plugin:device_detail_tab", args=[self.context["object"].pk]),
            },
        }


class SiteContent(PluginTemplateExtension):
    model = "dcim.site"

    def left_page(self):
        return "SITE CONTENT - LEFT PAGE"

    def right_page(self):
        return "SITE CONTENT - RIGHT PAGE"

    def full_width_page(self):
        return "SITE CONTENT - FULL WIDTH PAGE"

    def buttons(self):
        return "SITE CONTENT - BUTTONS"


class ExampleModelContent(PluginTemplateExtension):
    model = "example_plugin.examplemodel"
    template_name = "example_plugin/panel.html"

    def left_page(self):
        # You can use the render() method and pass it a template file and
        # context to populate it.
        return self.render(
            self.template_name,
            extra_context={
                "panel_title": "Plugin Left Page",
                "panel_body": "Now sliiiiide to the left... I'll show up after anything defined in the detail view template",
            },
        )

    def right_page(self):
        # You can also just send raw HTML.
        return """
        <div class="panel panel-default">
            <div class="panel-heading">
                <strong>Plugin Right Page</strong>
            </div>
            <div class="panel-body">
                <span>Check me out! I'll show up after anything defined in the detail view template.</span>
            </div>
        </div>
        """

    def full_width_page(self):
        return self.render(
            self.template_name,
            extra_context={
                "panel_title": "Plugin Full Width Page",
                "panel_body": "I'm a full width panel that shows up following other full-width panels defined in the detail view template.",
            },
        )

    def buttons(self):
        return """
        <a href="#" onClick="alert('I am from the plugin template_extension.')" class="btn btn-primary">
            <span class="mdi mdi-plus-thick" aria-hidden="true"></span>
            Plugin Button
        </a>
        """


# Don't forget to register your template extensions!
template_extensions = [ExampleModelContent, SiteContent, CircuitContent, DeviceContent]
