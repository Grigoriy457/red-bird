
import logging
from pydantic import BaseModel

import pytest

from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo
from redbird.base import BaseRepo

class LogRecord(BaseModel):
    name: str
    msg: str
    levelname: str
    levelno: int
    pathname: str
    filename: str
    module: str
    exc_info: str
    exc_text: str
    stack_info: str
    lineno: int
    funcName: str
    created: float
    msecs: float
    relativeCreated: float
    thread: int
    threadName: str
    processName: str
    process: int

    message: str
    formatted_message: str


@pytest.fixture(scope="function", autouse=True)
def logger(request):
    name = __name__ + '.'.join(request.node.nodeid.split("::")[1:])
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    yield logger
    logger.handlers = []

@pytest.fixture(scope="function", autouse=True)
def handler(logger):
    handler = RepoHandler(repo=MemoryRepo())
    logger.addHandler(handler)
    return handler

def test_handler_attrs(logger):
    handler = RepoHandler(repo=MemoryRepo())
    logger.addHandler(handler)

    assert hasattr(handler, "repo")
    assert isinstance(handler.repo, BaseRepo)

def test_info(logger):
    repo = MemoryRepo()
    handler = RepoHandler(repo=repo)
    assert handler.repo is repo

    logger.addHandler(handler)

    logger.info("a log", extra={"myextra": "something"})

    records = repo.filter_by().all()
    assert isinstance(records, list)
    assert 1 == len(records)
    
    record = records[0]

    assert isinstance(record, dict)
    assert set(record.keys()) == {
        'name', 'msg', 'args', 'levelname', 'levelno', 
        'pathname', 'filename', 'module', 
        'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName', 
        'created', 'msecs', 'relativeCreated', 
        'thread', 'threadName', 'processName', 'process', 
        'myextra', 'message', 'formatted_message'
    }

    expected_values = {
        'levelname': 'INFO',
        'levelno': 20,
        'threadName': 'MainThread',
        'processName': 'MainProcess',
        
        'args': (),
        'exc_info': None,
        'exc_text': None,
        'stack_info': None,

        'message': 'a log',
        'myextra': 'something',
        'formatted_message': 'a log',
    }

    actual_values = {key: val for key, val in record.items() if key in expected_values}
    assert actual_values == expected_values

def test_filter(logger):
    repo = MemoryRepo()
    handler = RepoHandler(repo=repo)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.info("an info", extra={"myextra": "something"})
    logger.debug("a debug", extra={"myextra": "something"})
    logger.warning("a warning", extra={"myextra": "something"})
    assert repo.filter_by().count() == 3

    records = repo.filter_by(levelname="INFO").all()
    assert len(records) == 1
    assert records[0]['levelname'] == 'INFO'

def test_set_level(logger):
    repo = MemoryRepo()
    handler = RepoHandler(repo=repo)
    handler.setLevel(logging.WARNING)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.info("an info", extra={"myextra": "something"})
    logger.debug("a debug", extra={"myextra": "something"})
    logger.warning("a warning", extra={"myextra": "something"})

    records = repo.filter_by().all()
    assert len(records) == 1
    assert records[0]['levelname'] == 'WARNING'