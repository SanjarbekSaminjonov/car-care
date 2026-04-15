import os
import time

import psycopg


def wait_for_postgres(max_attempts: int = 30, delay_seconds: int = 2) -> None:
    host = os.getenv("POSTGRES_HOST", "db")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    dbname = os.getenv("POSTGRES_DB", "car_care")
    user = os.getenv("POSTGRES_USER", "car_care")
    password = os.getenv("POSTGRES_PASSWORD", "car_care")

    for attempt in range(1, max_attempts + 1):
        try:
            with psycopg.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password,
                connect_timeout=3,
            ):
                print("PostgreSQL is ready")
                return
        except psycopg.OperationalError as error:
            if attempt == max_attempts:
                raise RuntimeError("PostgreSQL readiness check failed") from error
            print(f"PostgreSQL not ready yet (attempt {attempt}/{max_attempts})")
            time.sleep(delay_seconds)


if __name__ == "__main__":
    wait_for_postgres()
