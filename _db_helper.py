import sqlite3
import os
import logging
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class _db_query:
    @staticmethod
    def check_if_clime_exists(clime_id):
        try:
            cursor, conn = _db.connect()
            query = "SELECT * FROM climes WHERE id = ?"
            cursor.execute(query, (clime_id,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except sqlite3.Error as e:
            return False, str(e)
    @staticmethod
    def delete_claim_by_id(clime_id):
        try:
            logging.info(Fore.BLUE + f"Attempting to delete clime_id: {clime_id}")
            if  _db_query.check_if_clime_exists(clime_id):
                cursor, conn = _db.connect()
                query = "DELETE FROM climes WHERE id = ?"
                cursor.execute(query, (clime_id,))
                conn.commit()
                conn.close()
                logging.info(Fore.GREEN + f"Deleted clime_id: {clime_id} successfully")
                return True, "Deleted successfully"
            return False , "clime isnt exists"
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error deleting clime_id: {clime_id} - {e}")
            return False, str(e)

    @staticmethod
    def update_claim_status(status, claim_id):
        try:
            logging.info(Fore.BLUE + f"Updating status of claim_id: {claim_id} to {status}")
            cursor, conn = _db.connect()
            query = "UPDATE climes SET status = ? WHERE id = ?"
            cursor.execute(query, (status, claim_id))
            conn.commit()
            conn.close()
            logging.info(Fore.GREEN + f"Updated claim_id: {claim_id} successfully")
            return True, "Updated successfully"
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error updating status of claim_id: {claim_id} - {e}")
            return False, str(e)
    @staticmethod
    def retrieve_claim_by_id(claim_id):
        try:
            logging.info(Fore.BLUE + f"Retrieving claim by id: {claim_id}")
            cursor, conn = _db.connect()
            query = "SELECT * FROM climes WHERE id = ?"
            cursor.execute(query, (claim_id,))
            claim = cursor.fetchone()
            conn.close()
            if claim:
                logging.info(Fore.GREEN + f"Retrieved claim_id: {claim_id} successfully")
                return True, claim
            else:
                logging.warning(Fore.YELLOW + f"No claim found with ID {claim_id}")
                return False, f"No claim found with ID {claim_id}"
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error retrieving claim by id: {claim_id} - {e}")
            return False, str(e)

    @staticmethod
    def get_claim_data_report(status):
        try:
            print(status)
            logging.info(Fore.BLUE + "Retrieving all claims")
            cursor, conn = _db.connect()
            query = '''SELECT patient_name, diagnosis_code, procedure_code, status, SUM(claim_amount) AS total_claim_amount
                FROM climes 
                WHERE status = ?
                GROUP BY patient_name, diagnosis_code, procedure_code, status;'''
            cursor.execute(query,(status,))
            claims = cursor.fetchall()
            conn.close()
            logging.info(Fore.GREEN + "Retrieved all claims successfully")
            return True, claims
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error retrieving claims - {e}")
            return False, str(e)

    def get_claim_data(limit, page, diagnosis_code=None, procedure_code=None, status=None):
        try:
            logging.info(Fore.BLUE + "Retrieving claims with filters")
            cursor, conn = _db.connect()
            query = '''SELECT * FROM climes WHERE 
                        (diagnosis_code = ? OR diagnosis_code IS NULL) AND 
                        (procedure_code = ? OR procedure_code IS NULL) AND
                        (status = ? OR status IS NULL)
                        LIMIT ? OFFSET ?;'''

            params = (diagnosis_code, procedure_code, status, limit, (page - 1) * limit)
            cursor.execute(query, params)
            claims = cursor.fetchall()
            conn.close()
            logging.info(Fore.GREEN + "Retrieved claims with filters successfully")
            return True, claims
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error retrieving claims with filters - {e}")
            return False, str(e)

    @staticmethod
    def add_claim(patient_name, diagnosis_code, procedure_code, claim_amount):
        try:
            logging.info(Fore.BLUE + "Adding new claim")
            cursor, conn = _db.connect()
            query = "INSERT INTO climes (patient_name, diagnosis_code, procedure_code, claim_amount) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (patient_name, diagnosis_code, procedure_code, claim_amount))
            if cursor.rowcount > 0:  # Check if a row was inserted
                conn.commit()
                conn.close()
                logging.info(Fore.GREEN + "Claim added successfully")
                return True, "Claim created successfully"
            else:
                conn.close()
                logging.warning(Fore.YELLOW + "Failed to create claim")
                return False, "Failed to create claim"
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error adding claim - {e}")
            return False, str(e)

    @staticmethod
    def login(email, password):
        try:
            logging.info(Fore.BLUE + f"Logging in user with email: {email}")
            cursor, conn = _db.connect()
            query = "SELECT * FROM users WHERE email = ? AND password = ?"
            cursor.execute(query, (email, password))
            user_exists = cursor.fetchone() is not None
            conn.close()
            if user_exists:
                logging.info(Fore.GREEN + "User logged in successfully")
                return True
            else:
                logging.warning(Fore.YELLOW + "Login failed - Invalid credentials")
                return False
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error during login - {e}")
            return False, str(e)

    @staticmethod
    def check_exsists_email(email):
        try:
            logging.info(Fore.BLUE + f"Checking if email exists: {email}")
            cursor, conn = _db.connect()
            query = "SELECT * FROM users WHERE email = ?"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            conn.close()
            if result:
                logging.info(Fore.GREEN + f"Email {email} exists")
                return True  # return true if the email already exists
            else:
                logging.info(Fore.YELLOW + f"Email {email} does not exist")
                return False
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error checking email existence - {e}")
            return False, str(e)

    @staticmethod
    def add_user(name, email, password):
        try:
            logging.info(Fore.BLUE + f"Adding new user with email: {email}")
            if not _db_query.check_exsists_email(email):
                cursor, conn = _db.connect()
                query = "INSERT INTO users (name, email, password) VALUES (?, ?, ?)"
                cursor.execute(query, (name, email, password))
                conn.commit()
                conn.close()
                logging.info(Fore.GREEN + "User signed up successfully")
                return True, "User signed up successfully"
            else:
                logging.warning(Fore.YELLOW + f"User signup failed - Email {email} already exists")
                return False, "Email already exists"
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"Error adding user - {e}")
            return False, str(e)


class _db:
    @staticmethod
    def check_exists_db():
        return os.path.exists('claims.db')

    @staticmethod
    def connect():
        conn = sqlite3.connect('claims.db')
        cursor = conn.cursor()
        return cursor, conn

def _init__db():
    clime_query = '''
    CREATE TABLE IF NOT EXISTS climes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        diagnosis_code INT NOT NULL,
        procedure_code INT NOT NULL,
        claim_amount REAL NOT NULL,
        status INTEGER NOT NULL DEFAULT 0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    );
    '''
    if not _db.check_exists_db():
        cursor, conn = _db.connect()
        try:
            cursor.executescript(clime_query)
            conn.commit()
            conn.close()
            logging.info(Fore.GREEN + "[INFO] Database successfully initialized.")
            return True
        except sqlite3.Error as e:
            logging.error(Fore.RED + f"An error occurred during database initialization: {e}")
            return f"An error occurred: {e}"
    else:
        return False

# Call the function to initialize the database
def __main__():
    result = _init__db()
    return result

__main__()
