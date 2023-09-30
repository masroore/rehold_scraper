from peewee import *

_db = SqliteDatabase("rehold.db")


class BaseModel(Model):
    class Meta:
        database = _db


class City(BaseModel):
    name = CharField(max_length=160, null=True)
    slug = CharField(max_length=160, unique=True)


class Street(BaseModel):
    name = CharField(max_length=160)
    slug = CharField(max_length=240, unique=True)
    city = ForeignKeyField(City, backref="streets")


def city_get(name: str, slug: str) -> City:
    city = City.get_or_none(slug=slug)
    return city


def init_db():
    _db.connect()
    _db.create_tables(
        [
            City,
            Street,
        ],
    )
