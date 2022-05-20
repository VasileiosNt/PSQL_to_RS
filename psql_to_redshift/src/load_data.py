import random
import string
import datetime
from typing import Generator
import logging
from dotenv import load_dotenv
from pathlib import Path
import os
import psycopg2
import psycopg2.extras


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RowsGenerator:
    NUMBER_OF_RECORDS = 5 * (10**6)
    # Dummy init date
    START_DATE = datetime.datetime(year=1991, month=1, day=1)

    def __init__(self):
        logger.info("Generating random strings and timestamps")
        self.random_strings = tuple(
            self.generate_random_string(10, self.NUMBER_OF_RECORDS)
        )
        self.random_timestamps = tuple(
            self.generate_random_timestamp(self.START_DATE, self.NUMBER_OF_RECORDS)
        )
        logger.info("Done generating dummy data")

    @staticmethod
    def generate_random_string(
        length_of_string: int, records: int
    ) -> Generator[str, None, None]:
        while records > 0:
            yield "".join(
                random.choice(string.ascii_letters) for i in range(length_of_string)
            )
            records -= 1

    @staticmethod
    def generate_random_timestamp(
        starting_date: datetime.datetime, records: int
    ) -> Generator[str, None, None]:
        date = starting_date
        while records > 0:
            date += datetime.timedelta(minutes=random.randrange(60))
            yield date.strftime("%Y-%m-%d %H:%M:%S")
            records -= 1

    def get_rows(self) -> list:
        """
        Returns a list of tuples with random strings and timestamps,
        NOTE: last_update_timestamp & description strings/timestamps are shuffled from the pre-generated lists.
        """
        titles: tuple[str] = self.random_strings
        description = random.sample(titles, len(titles))
        published_timestamps: tuple[str] = self.random_timestamps
        last_updated_timestamps = random.sample(
            published_timestamps, len(published_timestamps)
        )
        return list(
            zip(titles, description, published_timestamps, last_updated_timestamps)
        )


if __name__ == "__main__":
    # Load the psql.env file to create the connection object
    psql_env_path: str = (
        f"{str(Path(__file__).parent.parent.absolute())}/infrastructure/env/psql.env"
    )
    load_dotenv(psql_env_path)

    generator = RowsGenerator()
    rows = generator.get_rows()
    logger.info(f"Number of rows generated: {len(rows)}")

    conn = psycopg2.connect(
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT"),
        database=os.environ.get("POSTGRES_DB"),
    )

    insert_statement = """
        insert into apps (title,description,published_timestamp,last_updated_timestamp) VALUES(%s,%s,%s,%s)
    """
    logger.info("Inserting to the db...")

    # use a context manager to ensure the connection is closed and auto-rollback in case of failure
    with conn.cursor() as cursor:
        psycopg2.extras.execute_batch(cursor, insert_statement, rows)
        conn.commit()
    logger.info("Insertion done successfully")
