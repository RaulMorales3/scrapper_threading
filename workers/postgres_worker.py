from os import getenv
import threading

from sqlalchemy import create_engine
from sqlalchemy.sql import text


class PostgresMasterScheduler(threading.Thread):
    def __init__(self, input_queue, **kwargs):
        super(PostgresMasterScheduler, self).__init__(**kwargs)
        self._input_queue = input_queue
        self.start()

    def run(self):
        while True:
            val = self._input_queue.get()
            if isinstance(val, str) and val.lower() == "done":
                break

            name, capital, population, extracted_time = val
            postgres_worker = PostgresWorker(
                name=name, capital=capital, population=population, extracted_time=extracted_time
            )
            postgres_worker.execute_query()


class PostgresWorker:
    def __init__(self, name: str, capital: str, population: int, extracted_time: str):
        self._name = name
        self._capital = capital
        self._population = population
        self._insert_time = extracted_time

        self._pg_user = getenv("PG_USER", "py_threads")
        self._pg_password = getenv("PG_PASSWORD", "py_threads")
        self._pg_host = getenv("PG_HOST", "localhost")
        self._pg_db = getenv("PG_DB", "py_threads")

        self._engine = create_engine(
            f"postgresql://{self._pg_user}:{self._pg_password}@{self._pg_host}/{self._pg_db}"
        )

    def _crete_insert_query(self):
        return """
        INSERT INTO countries (name, capital, population, insert_time) VALUES (:name, :capital, :population, :insert_time)
        """

    def execute_query(self):
        insert_query = self._crete_insert_query()

        print("insert_query", insert_query)
        with self._engine.connect() as conn:
            conn.execute(
                text(insert_query),
                dict(
                    name=self._name,
                    capital=self._capital,
                    population=self._population,
                    insert_time=str(self._insert_time),
                ),
            )
            conn.commit()
