import sqlite3
DATABASE_NAME = "applicants.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    """
    Create the applicants and cluster_decisions tables if they
    do not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Table 1: stores applicant information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            marks REAL NOT NULL,
            category_priority INTEGER NOT NULL,
            income_bracket INTEGER NOT NULL,
            distance_km REAL NOT NULL
        )
    """)
    # Table 2: stores the committee's decision about suspected duplicates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cluster_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_id INTEGER NOT NULL,
            decision TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_applicant(name, address, phone, marks,
                     category_priority, income_bracket, distance_km):
    """
    Insert one applicant into the database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO applicants
        (name, address, phone, marks, category_priority,
         income_bracket, distance_km)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        address,
        phone,
        marks,
        category_priority,
        income_bracket,
        distance_km
    ))
    conn.commit()
    conn.close()


def get_all_applicants():
    """
    Return all applicants from the database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, address, phone, marks,
               category_priority, income_bracket, distance_km
        FROM applicants
        ORDER BY id
    """)
    applicants = cursor.fetchall()
    conn.close()
    return applicants


def clear_applicants():
    """
    Delete all applicant records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applicants")
    conn.commit()
    conn.close()


def save_cluster_decision(cluster_id, decision):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM cluster_decisions
        WHERE cluster_id = ?
    """, (cluster_id,))
    cursor.execute("""
        INSERT INTO cluster_decisions (cluster_id, decision)
        VALUES (?, ?)
    """, (cluster_id, decision))
    conn.commit()
    conn.close()


def get_cluster_decisions():
    """
    Return all saved cluster decisions.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, cluster_id, decision
        FROM cluster_decisions
        ORDER BY id
    """)
    decisions = cursor.fetchall()
    conn.close()
    return decisions
