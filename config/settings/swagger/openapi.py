from typing import Optional

from drf_spectacular.drainage import warn
from drf_spectacular.openapi import AutoSchema as _AutoSchema
from drf_spectacular.plumbing import (
    build_array_type,
    build_basic_type,
    build_examples_list,
    build_parameter_type,
    force_instance,
    is_basic_serializer,
    is_basic_type,
)
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.utils import OpenApiExample, OpenApiParameter


class AutoSchema(_AutoSchema):
    def _get_pagination(self):
        view = getattr(self.view, "VIEWS_BY_METHOD", {}).get(self.method, None)
        pagination_class = getattr(view.__self__, "Pagination", None)
        if pagination_class:
            return pagination_class()
        return None

    def _get_renders(self):
        view = getattr(self.view, "VIEWS_BY_METHOD", {}).get(self.method, None)
        renderer_classes = getattr(view.__self__, "renderer_classes", None)
        if renderer_classes:
            return renderer_classes
        return None

    def _get_parameter_example(self, parameter_name):
        result = []
        examples = self.get_examples()

        for example in examples:
            if getattr(example, "request_only", False):
                continue
            if getattr(example, "response_only", False):
                continue
            if getattr(example, "field_name", None) == parameter_name:
                result.append(example)
        return result

    def _get_response_for_code(self, serializer, status_code, media_types=None, direction="response"):
        response = super()._get_response_for_code(serializer, status_code, media_types, direction)

        if (
            self._get_pagination()
            and self.method == "GET"
            and ("200" <= status_code < "300" or spectacular_settings.ENABLE_LIST_MECHANICS_ON_NON_2XX)
        ):
            pagination = self._get_pagination()
            response["content"]["application/json"]["schema"] = pagination.get_paginated_response_schema(
                response["content"]["application/json"]["schema"]
            )

        if self._get_renders():
            renders = self._get_renders()
            for render in renders:
                if hasattr(render(), "get_render_schema"):
                    response["content"]["application/json"]["schema"] = render().get_render_schema(
                        response["content"]["application/json"]["schema"],
                        int(status_code),
                    )
        return response

    def _process_override_parameters(self, direction="request"):
        result = {}
        for parameter in self.get_override_parameters():
            if isinstance(parameter, OpenApiParameter):
                if parameter.response:
                    continue
                if is_basic_type(parameter.type):
                    schema = build_basic_type(parameter.type)
                elif is_basic_serializer(parameter.type):
                    schema = self.resolve_serializer(parameter.type, direction).ref
                elif isinstance(parameter.type, dict):
                    schema = parameter.type
                else:
                    warn(f'unsupported type for parameter "{parameter.name}". Skipping.')
                    continue

                if parameter.many:
                    if is_basic_type(parameter.type):
                        schema = build_array_type(schema)
                    else:
                        warn(
                            f'parameter "{parameter.name}" has many=True and is not a basic type. '
                            f"many=True only makes sense for basic types. Ignoring."
                        )

                if parameter.exclude:
                    result[parameter.name, parameter.location] = None
                else:
                    result[parameter.name, parameter.location] = build_parameter_type(
                        name=parameter.name,
                        schema=schema,
                        location=parameter.location,
                        required=parameter.required,
                        description=parameter.description,
                        enum=parameter.enum,
                        pattern=parameter.pattern,
                        deprecated=parameter.deprecated,
                        style=parameter.style,
                        explode=parameter.explode,
                        default=parameter.default,
                        allow_blank=parameter.allow_blank,
                        examples=build_examples_list(parameter.examples),
                        extensions=parameter.extensions,
                    )
            elif is_basic_serializer(parameter):
                parameter = force_instance(parameter)
                mapped = self._map_serializer(parameter, "request")
                for property_name, property_schema in mapped["properties"].items():
                    field = parameter.fields.get(property_name)
                    parameter_example = self._get_parameter_example(property_name)
                    result[property_name, OpenApiParameter.QUERY] = build_parameter_type(
                        name=property_name,
                        schema=property_schema,
                        description=property_schema.pop("description", None),
                        location=OpenApiParameter.QUERY,
                        allow_blank=getattr(field, "allow_blank", True),
                        required=field.required,
                        examples=build_examples_list(parameter_example),
                    )
            else:
                warn(f"could not resolve parameter annotation {parameter}. Skipping.")
        return result


class ParameterOpenApiExample(OpenApiExample):
    def __init__(self, field_name: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = field_name
