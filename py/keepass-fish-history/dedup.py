import json
from dataclasses import dataclass
from typing import Any, Callable, Type, TypeVar, get_args

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

# The generic type T is defined here because we cannot define it on the base class
# That causes the type checker to go crazy and mark the method
# `__get_parse_method` as unknown and unused.
T = TypeVar("T", bound="Base")
# We need to use a function to check for Self reference in annotations
# The reason is that static type checkers will think that we are using Self in
# forbidden contexts like when using cls or self typed to a class that is not Self
# but we are in fact just searching for the reference of Self in any annotation
self_checker: Callable[[Any], bool] = lambda annotation: annotation is Self


class Base:
    @classmethod
    def __get_parse_method(
        cls: Type[T], field: str
    ) -> Callable[[dict[str, Any]], T | list[T]] | None:
        """Retrieve the parse method for a field's type if it exists."""
        annotation = get_args(cls.__annotations__.get(field))
        is_iterable = False
        if len(annotation) < 1:
            annotation = cls.__annotations__.get(field)
        else:
            annotation = annotation[0]
            is_iterable = True
        if self_checker(annotation):
            annotation = cls
        method = getattr(annotation, "parse", None)
        if is_iterable and method:
            return lambda data: [method(item) for item in data]
        return method

    @classmethod
    def parse(cls: Type[T], data: dict[str, Any]) -> T:
        """Parse a dictionary into an instance of the class."""
        kwargs = {}
        for field in cls.__dict__.get("__match_args__", []):
            value = data.get(field)
            if value is None:
                value = data.get(f"{field}_")
            parse_method = cls.__get_parse_method(field)
            if value is not None and parse_method:
                value = parse_method(value)
            kwargs[field] = value
        return cls(**kwargs)

    def as_dict(self) -> dict[str, Any]:
        """Convert the instance into a dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if hasattr(value, "as_dict"):
                result[key] = value.as_dict()
            elif isinstance(value, list) and all(
                hasattr(item, "as_dict") for item in value
            ):
                result[key] = [item.as_dict() for item in value]
            else:
                result[key] = value
        return result

    def as_json(self, indent=4, ensure_ascii=False) -> str:
        """Convert the instance into a JSON string."""
        return json.dumps(self.as_dict(), indent=indent, ensure_ascii=ensure_ascii)


@dataclass
class Command(Base):
    cmd: str
    when: int
    paths: list[str]


def __dedup(data: list[dict[str, str]]) -> list[Command]:
    uniq: list[Command] = []
    queries: list[str] = []
    for idx, item in enumerate(data):
        command = Command.parse(item)
        pseudo = ([] if command.paths is None else command.paths) + [command.cmd]
        query = "-".join(pseudo)
        if query not in queries:
            queries.append(query)
            uniq.append(command)
    return uniq


FISH_YAML_COMMAND_TEMPLATE_WITH_PATH = """- cmd: {COMMAND}
  when: {WHEN}
  paths:
{PATHS}"""

FISH_YAML_COMMAND_TEMPLATE_WITHOUT_PATH = """- cmd: {COMMAND}
  when: {WHEN}"""


def as_fish_yaml(data: list[Command]) -> str:
    root = ""
    for command in data:
        if command.paths is None or len(command.paths) < 1:
            value = FISH_YAML_COMMAND_TEMPLATE_WITHOUT_PATH.format(
                COMMAND=command.cmd, WHEN=command.when
            )
            root += f"{value}\n"
            continue
        path_str = ""
        for path in command.paths:
            path_str += f"    - {path}\n"
        path_str = path_str.rstrip("\n")
        value = FISH_YAML_COMMAND_TEMPLATE_WITH_PATH.format(
            COMMAND=command.cmd, WHEN=command.when, PATHS=path_str
        )
        root += f"{value}\n"
    return root


def parse_content(contents: str):
    items = []

    current_content = {}
    paths: list[str] = []
    is_in_path_scope = True
    for i, line in enumerate(contents.strip().split("\n")):
        if not line:
            continue
        if line.startswith("- cmd"):
            is_in_path_scope = False
            current_content["paths"] = paths
            paths = []
            if i != 0:
                items.append(current_content)
            value = line.split("- cmd: ")[1]
            current_content = {"cmd": value}
            continue
        if line.strip().startswith("when"):
            is_in_path_scope = False
            current_content["when"] = line.split("  when: ")[1]
            continue
        if line.strip().startswith("paths"):
            is_in_path_scope = True
            continue
        if is_in_path_scope and line.strip().startswith("-"):
            paths.append(line.strip().split("- ")[1])
    items.append(current_content)
    return items


def dedup(contents: str) -> str:
    data = parse_content(contents)
    commands = __dedup(data)
    return as_fish_yaml(commands)
