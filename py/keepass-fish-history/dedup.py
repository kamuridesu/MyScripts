from dataclasses import dataclass
from typing import TypedDict

ItemType = TypedDict("ItemType", {"cmd": str, "when": int, "paths": list[str]})


@dataclass
class Command:
    cmd: str
    when: int
    paths: list[str]


def load_exclusion_list(exclusion: str) -> list[str]:
    return exclusion.strip().splitlines()


def has_term_from_exclusion(exclusion_list: list[str], command: Command) -> bool:
    if len(exclusion_list) < 1:
        return False
    for term in exclusion_list:
        term = term.lower()
        if term in command.cmd.lower():
            return True
        if command.paths != None and any(
            term in path.lower() for path in command.paths
        ):
            return True
    return False


def __dedup(data: list[ItemType], exclusion: str) -> list[Command]:
    uniq: list[Command] = []
    queries: list[str] = []
    total = len(data)
    exclude = load_exclusion_list(exclusion)
    for _, item in enumerate(data):
        command = Command(**item)
        if command.cmd is None:
            continue
        if has_term_from_exclusion(exclude, command):
            print(f"Skipping command {command.cmd}")
            continue
        query = "-".join(
            ([] if command.paths is None else command.paths) + [command.cmd]
        )
        if query not in queries:
            queries.append(query)
            uniq.append(command)
    uniq.sort(key=lambda cmd: cmd.when)
    print(f"Pruned items: {total - len(uniq)}")
    return uniq


FISH_YAML_COMMAND_TEMPLATE = """- cmd: {COMMAND}
  when: {WHEN}"""


def as_fish_yaml(data: list[Command]) -> str:
    root = ""
    for command in data:
        value = FISH_YAML_COMMAND_TEMPLATE.format(
            COMMAND=command.cmd, WHEN=command.when
        )

        if command.paths != None and len(command.paths) > 0:
            template = "\n  paths:\n{PATHS}"
            path_str = "".join(f"    - {path}\n" for path in command.paths).rstrip("\n")
            value += template.format(PATHS=path_str)
        root += f"{value}\n"
    return root


def parse_content(contents: str) -> list[ItemType]:
    items: list[ItemType] = []

    current_item: ItemType | None = None
    for line in contents.strip().split("\n"):
        stripped_line = line.strip()
        if not stripped_line:
            continue

        if stripped_line.startswith("- cmd:"):
            if current_item:
                items.append(current_item)
            value = line.split(":", 1)[1].strip()
            current_item = {"cmd": value, "when": 0, "paths": []}

        elif current_item:
            if stripped_line.startswith("when:"):
                value = stripped_line.split(":", 1)[1].strip()
                current_item["when"] = int(value)
            elif stripped_line.startswith("-"):
                value = stripped_line.split("-", 1)[1].strip()
                current_item["paths"].append(value)

        if current_item:
            items.append(current_item)

    return items


def dedup(contents: str, exclusion: str) -> str:
    data = parse_content(contents)
    commands = __dedup(data, exclusion)
    return as_fish_yaml(commands)
