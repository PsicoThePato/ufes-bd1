from peewee import Model


class BaseModel(Model):
    class Meta:
        legacy_table_names = False
