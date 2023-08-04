from datetime import datetime
from typing import Any, Callable, Generic, TypeVar, Union
from zoneinfo import ZoneInfo

import orjson
from pydantic import model_validator, ConfigDict, BaseModel

SchemaType = TypeVar("SchemaType", bound=BaseModel)


def orjson_dumps(v: Any, *, default: Callable[[Any], Any] | None) -> str:
    return orjson.dumps(v, default=default).decode()


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class ORJSONModel(BaseModel):
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={datetime: convert_datetime_to_gmt}, populate_by_name=True)

    @model_validator(mode="after")
    @classmethod
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, Any]:
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(k, datetime)
        }

        return {**data, **datetime_fields}


class APIResponse(BaseModel, Generic[SchemaType]):
    success: bool = True
    code: str = "200"
    message: str = "OK"
    data: Union[SchemaType, Any] = None
