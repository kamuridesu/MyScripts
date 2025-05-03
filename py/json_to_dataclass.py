import json

template = """@dataclass
class {CLASS_NAME}:
    {FIELDS}

    @staticmethod
    def parse(data: dict) -> "{CLASS_NAME}":
        kwargs = {{}}
        external_fields: dict[str, Callable[[dict[Any, Any]], Any]] = {EXTERNAL_FIELDS}
        for field in {CLASS_NAME}.__dict__.get("__match_args__", []):
            value: Any = data.get(field)
            if (func := external_fields.get(field)) is not None:
                value = func(value)
            kwargs[field] = value
        return {CLASS_NAME}(**kwargs)
"""


def create_class(root_name: str, data: dict | list):

    classes = []

    def parse_dict_class(name: str, data: dict):
        fields = []
        external_fields = []
        for k, v in data.items():
            if isinstance(v, dict):
                classes.append(parse_dict_class(k.capitalize(), v))
                fields.append(f"{k}: {k.capitalize()}")
                external_fields.append(f'"{k}": {k.capitalize()}.parse')
                continue
            if isinstance(v, list) and v:
                types = list(set([c.__class__.__name__ if c is not None else None for c in v]))
                if all([t == "dict" for t in types]):
                    classes.append(parse_dict_class(k.capitalize(), v[0]))
                    fields.append(f"{k}: list[{k.capitalize()}]")
                    external_fields.append(f'"{k}": lambda x: [{k.capitalize()}.parse(f) for f in x]')
                    continue
                fields.append(f"{k}: list[{' | '.join(types)}]")
                continue
            _type = v.__class__.__name__ if v is not None else "Any"
            fields.append(f"{k}: {_type}")
            continue
        return template.format(
            CLASS_NAME=name,
            FIELDS="\n    ".join(fields),
            EXTERNAL_FIELDS=r"{"
            + "\n            "
            + ",\n            ".join(external_fields)
            + "\n        "
            + r"}",
        )

    if isinstance(data, dict):
        classes.append(parse_dict_class(root_name, data))

    return "\n\n".join(classes)
