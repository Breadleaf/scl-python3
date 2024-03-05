import typing

from ._helpers import load_helper, dump_helper

def loads(config_text: str) -> dict:
    return load_helper(config_text)


def load(file: typing.TextIO) -> dict:
    return loads(file.read())


def dumps(config: dict) -> str:
    return dump_helper(config)


def dump(config: dict, file: typing.TextIO) -> None:
    config.write(dumps(config))
