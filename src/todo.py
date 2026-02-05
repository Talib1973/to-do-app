from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False
