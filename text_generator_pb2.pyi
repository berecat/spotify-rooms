from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateRequest(_message.Message):
    __slots__ = ["max_length", "text"]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    max_length: int
    text: str
    def __init__(self, text: _Optional[str] = ..., max_length: _Optional[int] = ...) -> None: ...

class GenerateResponse(_message.Message):
    __slots__ = ["text"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class GenerateStreamedRequest(_message.Message):
    __slots__ = ["intermediate_result_interval_ms", "max_length", "text"]
    INTERMEDIATE_RESULT_INTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    intermediate_result_interval_ms: int
    max_length: int
    text: str
    def __init__(self, text: _Optional[str] = ..., max_length: _Optional[int] = ..., intermediate_result_interval_ms: _Optional[int] = ...) -> None: ...
