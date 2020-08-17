import peewee
from playhouse import migrate


class SQLAdapter:

    @classmethod
    def sqlite(cls, database_name='sqlite.db'):
        return peewee.SqliteDatabase(database_name)

    @classmethod
    def mysql(cls, database_name, host, user, password, port=3306):
        return peewee.MySQLDatabase(
            database=database_name,
            host=host,
            user=user,
            passwd=password,
            port=port
        )

    @classmethod
    def postgresql(cls, database_name, host, user, password, port=3306):
        return peewee.PostgresqlDatabase(
            database=database_name,
            host=host,
            user=user,
            passwd=password,
            port=port
        )


class MigratorAdapter:
    def __init__(self, db: SQLAdapter):
        self._db = db

    @property
    def migrator(self):
        if isinstance(self._db, peewee.SqliteDatabase):
            return migrate.SqliteMigrator(self._db)
        elif isinstance(self._db, peewee.MySQLDatabase):
            return migrate.MySQLMigrator(self._db)
        elif isinstance(self._db, peewee.PostgresqlDatabase):
            return migrate.PostgresqlMigrator(self._db)
        else:
            ValueError(self._db)
