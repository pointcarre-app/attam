import logging
import psycopg2
from psycopg2.extras import Json
from typing import Optional, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)


class PostgresManager:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def safely_execute(self, query: str, vars: tuple = None) -> bool:
        """
        Executes a query safely with commit/rollback handling.
        """
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            try:
                cur.execute(query, vars)
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"Error executing query: {e}")
                # Re-raise or return False depending on desired behavior.
                # The inspiration code raised exception in some places, caught in others.
                # Here we log and re-raise to let caller handle critical failures.
                raise e
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    def kill_connections(self):
        """
        Terminates all other connections to the database.
        """
        query = """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = current_database()
            AND pid <> pg_backend_pid();
        """
        try:
            self.safely_execute(query)
            logger.info("Killed all other connections to the database.")
        except Exception as e:
            logger.warning(f"Failed to kill connections: {e}")

    def create_raw_trame_table_if_not_exists(self):
        """
        Creates the raw_trame table if it does not exist.
        """
        query = """
            CREATE TABLE IF NOT EXISTS raw_trame (
                id SERIAL PRIMARY KEY,
                username VARCHAR NOT NULL,
                title VARCHAR(256),
                slug VARCHAR(256),
                saving_origin VARCHAR DEFAULT 'manual',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
                modified_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
                md_content TEXT NOT NULL,
                piece_count INTEGER NOT NULL,
                metadata JSONB
            )
        """
        self.safely_execute(query)
        logger.info("Table 'raw_trame' verified/created.")

    def save_raw_trame(
        self,
        username: str,
        md_content: str,
        piece_count: int,
        title: Optional[str] = None,
        slug: Optional[str] = None,
        saving_origin: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Saves a record to the raw_trame table.
        """
        self.kill_connections()

        query = """
            INSERT INTO raw_trame (
                username,
                title,
                slug,
                saving_origin,
                md_content,
                piece_count,
                metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        self.safely_execute(
            query,
            vars=(
                username,
                title,
                slug,
                saving_origin,
                md_content,
                piece_count,
                Json(metadata) if metadata is not None else None,
            ),
        )
        logger.info(f"Saved raw_trame for user {username}")
