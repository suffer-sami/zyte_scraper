import psycopg2
from psycopg2 import sql
import json
import os

class DatabaseConnection:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.conn = None

    def _load_config(self, config_path):
        """Load database configuration from JSON file"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in configuration file")

    def connect(self):
        """Create a new database connection"""
        try:
            self.conn = psycopg2.connect(**self.config)
            return self.conn
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def execute_query(self, query, commit=True):
        """Execute a query and optionally commit"""
        if not self.conn or self.conn.closed:
            self.connect()

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                if commit:
                    self.conn.commit()
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise e

    def close(self):
        """Close the database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()