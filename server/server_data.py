"""A module to handle user name -> password storing in a database.

unqiue salted encrpytion is used for each user, stored in seperate databases
"""
import sqlite3
from enum import Enum, auto
from shared_python.shared_database.passwords import hash_password, is_correct_password
from shared_server_client_coms.authenticate_params import *


class DatabaseInsertState(Enum):
    """Enum that represents database key entry"""
    SUCCESS = auto()
    DATABASE_ERROR = auto()
    ALREADY_EXISTS = auto()


class _PasswordDatabase():
    def __init__(self) -> None:
        self._connection = sqlite3.connect("salts.db", check_same_thread=False)
        self._cursor = self._connection.cursor()

        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            user_id INT PRIMARY KEY,
            salt varbinary(1024) NOT NULL UNIQUE
        )
        """)

        self._connection.commit()

    def get_salt(self, user_id: int) -> bytes:
        """Retrieve the salt used to encrypt the password that matches the user_id
        from the database
        """
        self._cursor.execute(f"""
            SELECT salt 
            FROM passwords
            WHERE user_id={user_id}
        """)
        ret = self._cursor.fetchone()
        if ret is not None:
            return ret[0]

    def add_salt(self, user_id: int, salt: bytes):
        """add a user_id with a matching salt used to encrypt the password, into the database"""
        self._cursor.execute("""
            INSERT INTO passwords(user_id, salt) VALUES
            (?,?);""", (user_id, salt))

        self._connection.commit()


class UserDatabase():
    """A class that represents the user -> password database, with the salt database
    hidden in the back-end
    """

    def __init__(self) -> None:
        self._connection = sqlite3.connect("users.db", check_same_thread=False)
        self._cursor = self._connection.cursor()
        self._password_database = _PasswordDatabase()

        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER NOT NULL,
            username varchar(255) NOT NULL UNIQUE,
            password varbinary(1024) NOT NULL,
            PRIMARY KEY (user_id)
        )
        """)

        self._connection.commit()

    def _get_user_id(self, username: str) -> int:
        self._cursor.execute(f"""
            SELECT user_id 
            FROM users
            WHERE username='{username}'
        """)
        ret = self._cursor.fetchone()
        if ret is not None:
            return ret[0]

    def _get_user_password(self, user_id: int) -> str:
        self._cursor.execute(f"""
            SELECT password 
            FROM users
            WHERE user_id='{user_id}'
        """)
        ret = self._cursor.fetchone()
        if ret is not None:
            return ret[0]

    def inser_user(self, username: str, password: str) -> DatabaseInsertState:
        """Insert a username / password into the database"""
        reuslt = self._get_user_id(username)

        if reuslt:
            return DatabaseInsertState.ALREADY_EXISTS

        else:
            salt, password = hash_password(password)

            self._cursor.execute("""
                INSERT INTO users(username, password) VALUES
                (?,?);""", (username, password))

            self._connection.commit()
            self._password_database.add_salt(self._get_user_id(username), salt)

            return DatabaseInsertState.SUCCESS

    def confirm_password(self, username: str, password: str) -> AuthStatus:
        """Determines if the username matches the password stored in the database"""
        user_id = self._get_user_id(username)
        if user_id is None:
            return AuthStatus.INCORRECT_USER

        hashed_password = self._get_user_password(user_id)
        salt = self._password_database.get_salt(user_id)

        if is_correct_password(salt, hashed_password, password):
            return AuthStatus.SUCCESS
        else:
            return AuthStatus.INCORRECT_PASSWORD
