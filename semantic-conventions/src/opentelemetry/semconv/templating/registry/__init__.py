#   Copyright The OpenTelemetry Authors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import io
import re
import typing

from opentelemetry.semconv.model.semantic_attribute import (
    EnumAttributeType,
    EnumMember,
    SemanticAttribute,
    StabilityLevel,
)
from opentelemetry.semconv.model.semantic_convention import (
    BaseSemanticConvention,
    SemanticConventionSet,
)
from opentelemetry.semconv.model.utils import ID_RE
from opentelemetry.semconv.templating.markdown.options import MarkdownOptions


class RenderContext:
    def __init__(self):
        self.enums = []
        self.notes = []

    def clear_table_generation(self):
        self.notes = []
        self.enums = []

    def add_note(self, msg: str):
        self.notes.append(msg)

    def add_enum(self, attr: SemanticAttribute):
        self.enums.append(attr)


class RegistryRenderer:
    p_start = re.compile("<!--\\s*semconv\\s+(.+)-->")
    p_semconv_selector = re.compile(
        rf"(?P<semconv_id>{ID_RE.pattern})?"
    )
    p_end = re.compile("<!--\\s*endsemconv\\s*-->")
    default_break_conditional_labels = 50

    prelude = "<!-- semconv {} -->\n"
    table_headers = "| Attribute  | Type | Description  | Examples  | Stability |\n|---|---|---|---|---|\n"

    def __init__(
        self, semconvset: SemanticConventionSet, options=MarkdownOptions()
    ):
        self.options = options
        self.render_ctx = RenderContext()
        self.semconvset = semconvset

    def to_markdown_attribute_table(
        self, root_namespace: str, attributes: list[SemanticAttribute], output: io.StringIO
    ):
        first = True
        attributes_by_ns = self._groupby_namespace(attributes)
        for ns in sorted(attributes_by_ns.keys()):
            self.render_ctx.clear_table_generation()
            self.to_namespace_description(root_namespace, ns, output, first)
            first = False
            for attr in sorted(attributes_by_ns[ns], key=lambda a: a.fqn):
                self.to_registry_attr(attr, output)
            self.to_markdown_notes(output)
            self.to_markdown_enum(output)
            output.write("\n")

    def to_namespace_description(
        self, root_ns: str, ns: str, output: io.StringIO, first: bool
    ):
        if first:
            output.write(f"## {root_ns}\n\n")

        if (root_ns != ns):
            output.write(f"### {ns}\n\n")

        #output.write(f"{semconv.brief}\n\n")
        #if semconv.note is not None and semconv.note != "":
        #    output.write(f"{semconv.note}\n\n")
        output.write(RegistryRenderer.table_headers)


    def to_markdown_notes(self, output: io.StringIO):
        """Renders notes after a Semantic Convention Table
        :return:
        """
        counter = 1
        for note in self.render_ctx.notes:
            output.write(f"\n**[{counter}]:** {note}\n")
            counter += 1

    def to_markdown_enum(self, output: io.StringIO):
        """Renders enum types after a Semantic Convention Table
        :return:
        """
        attr: SemanticAttribute
        for attr in self.render_ctx.enums:
            enum = typing.cast(EnumAttributeType, attr.attr_type)
            output.write(f"`{attr.fqn}` ")
            if enum.custom_values:
                output.write(
                    "has the following list of well-known values."
                    + " If one of them applies, then the respective value MUST be used,"
                    + " otherwise a custom value MAY be used."
                )
            else:
                output.write("MUST be one of the following:")
            output.write("\n\n")
            output.write("| Value  | Description |\n|---|---|")
            member: EnumMember
            counter = 1
            notes = []
            for member in enum.members:
                description = member.brief
                if member.note:
                    description += f" [{counter}]"
                    counter += 1
                    notes.append(member.note)
                output.write(f"\n| `{member.value}` | {description} |")
            counter = 1
            if not notes:
                output.write("\n")
            for note in notes:
                output.write(f"\n\n**[{counter}]:** {note}")
                counter += 1
            if notes:
                output.write("\n")

    def _get_stability_message(self,
        attribute: SemanticAttribute,
    ):
        stability_msg = f"{self.options.md_snippet_by_stability_level[attribute.stability]}<br>"
        if attribute.deprecated:
            if "deprecated" in attribute.deprecated.lower():
                stability_msg = f"**{attribute.deprecated}**<br>"
            else:
                stability_msg = self.options.md_snippet_by_stability_level[
                    StabilityLevel.DEPRECATED
                ].format(attribute.deprecated)
        return stability_msg

    def to_registry_attr(
        self,
        attribute: SemanticAttribute,
        output: io.StringIO,
    ):
        """
        This method renders attributes as registry table entry
        """
        name = f"<a name=\"{attribute.fqn}\">`{attribute.fqn}`</a>"
        attr_type = (
            "enum"
            if isinstance(attribute.attr_type, EnumAttributeType)
            else attribute.attr_type
        )
        stability = self._get_stability_message(attribute)
        description = attribute.brief
        if attribute.note:
            self.render_ctx.add_note(attribute.note)
            description += f" [{len(self.render_ctx.notes)}]"
        examples = ""
        if isinstance(attribute.attr_type, EnumAttributeType):
            self.render_ctx.add_enum(attribute)
            example_list = attribute.examples if attribute.examples else ()
            examples = (
                "; ".join(f"`{ex}`" for ex in example_list)
                if example_list
                else f"`{attribute.attr_type.members[0].value}`"
            )
            # Add better type info to enum
            if attribute.attr_type.custom_values:
                attr_type = attribute.attr_type.enum_type
            else:
                attr_type = attribute.attr_type.enum_type
        elif attribute.attr_type:
            example_list = attribute.examples if attribute.examples else []
            # check for array types
            if attribute.attr_type.endswith("[]"):
                examples = "`[" + ", ".join(f"{ex}" for ex in example_list) + "]`"
            else:
                examples = "; ".join(f"`{ex}`" for ex in example_list)

        output.write(
            f"| {name} | {attr_type} | {description} | {examples} | {stability} |\n"
        )

    def render_registry(self):
        md_filename = "/dst/registry.md"
        output = io.StringIO()        
        output.write(f"# OpenTelemetry attributes registry\n\n")
        all_attributes = []
        for semconv in self.semconvset.models.values():
            all_attributes.extend([a for a in semconv.attributes if a.is_local and a.ref is None])
        attributes_by_root = self._groupby_root_namespace(all_attributes)
        
        for root_ns in sorted(attributes_by_root.keys()):
            if len(attributes_by_root.get(root_ns)) > 0:
                self.to_markdown_attribute_table(root_ns, attributes_by_root.get(root_ns), output)
        
        with open(md_filename, mode="w", encoding="utf-8") as md_file:
            md_file.write(output.getvalue())

    def _groupby_root_namespace(self, attributes: list[SemanticAttribute]):
        # group by root_namespace
        attributes_by_root = {}
        for attribute in attributes:
            if attribute.root_namespace not in attributes_by_root:
                attributes_by_root[attribute.root_namespace] = []
            attributes_by_root[attribute.root_namespace].append(attribute)
        return attributes_by_root

    def _groupby_namespace(self, attributes: list[SemanticAttribute]):
        attributes_by_ns = {}
        for attribute in attributes:
            if attribute.namespace not in attributes_by_ns:
                attributes_by_ns[attribute.namespace] = []
            attributes_by_ns[attribute.namespace].append(attribute)
        return attributes_by_ns