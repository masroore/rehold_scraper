from peewee import *

_db = SqliteDatabase("rehold.db")


class BaseModel(Model):
    class Meta:
        database = _db


class City(BaseModel):
    name = CharField(unique=True)


def init_db():
    _db.connect()
    _db.create_tables(
        [City],
    )
