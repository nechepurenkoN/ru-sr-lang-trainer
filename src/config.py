import dataclasses
import os


@dataclasses.dataclass
class Config:
    token: str
    read_timeout: int
    write_timeout: int


def default_config() -> Config:
    return Config(
        os.getenv("TOKEN"),
        10,
        10
    )


class State:
    MAIN, HELP, TOPIC, EXERCISE = range(3)
