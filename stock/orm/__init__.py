import peewee

from . import models

__all__ = [models]


class SQLFactory:
    @classmethod
    def sqlite(cls, database_name="sqlite.db"):
        return peewee.SqliteDatabase(database_name)

    @classmethod
    def mysql(cls, database_name, host, user, password, port=3306):
        return peewee.MySQLDatabase(database=database_name, host=host, user=user, passwd=password, port=port)

    @classmethod
    def postgresql(cls, database_name, host, user, password, port=3306):
        return peewee.PostgresqlDatabase(database=database_name, host=host, user=user, passwd=password, port=port)
