from dataclasses import dataclass


@dataclass
class Finding:
    file: str
    line: int
    rule_id: str
    criterion: str
    message: str
    snippet: str
