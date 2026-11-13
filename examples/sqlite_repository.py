"""Example application-owned repository using the managed SQLite connector."""

from contextlib import nullcontext

from nikhi.adhara_sutra import Application, SQLiteDatabase


class ItemRepository:
    def __init__(self, database):
        self.database = database
        database.execute("CREATE TABLE IF NOT EXISTS items (name TEXT PRIMARY KEY)")

    def add(self, name):
        with self.database.transaction():
            self.database.execute("INSERT INTO items (name) VALUES (?)", (name,))

    def list_names(self):
        return [row["name"] for row in self.database.query("SELECT name FROM items ORDER BY name")]


def create_app(name="repository_example", path=":memory:"):
    app = Application(name, "1.0")
    app.service("database", lambda context: SQLiteDatabase(path))
    app.service("items", lambda context: nullcontext(ItemRepository(context.get_service("database"))),
                depends_on=("database",))

    @app.action("items.add")
    def add(payload, context):
        context.get_service("items").add(payload["name"])
        return {"added": payload["name"]}

    @app.action("items.list")
    def list_items(payload, context):
        return {"items": context.get_service("items").list_names()}

    return app


if __name__ == "__main__":
    raise SystemExit(create_app().run())
