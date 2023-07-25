from pydantic import BaseModel

from example_lib_core.schema import Model


class UnusedModel(BaseModel):
    # to have import from pydantic
    pass


class ExtendedModel(Model):
    name: str
