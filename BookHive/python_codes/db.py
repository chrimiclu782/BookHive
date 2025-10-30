"""
Database Connection Module

This module provides database connection functionality for the BookHive library system.
It establishes connections to the MySQL database using the mysql.connector library.
"""

import mysql.connector

def connect_db():
    """
    Establish and return a connection to the BookHive database.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="BookHiveDB"
    )
