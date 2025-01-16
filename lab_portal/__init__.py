import MySQLdb
from django.conf import settings
from django.core.management import call_command


def create_database_if_not_exists():
    # Fetch database configuration
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT'] or 3306

    # Connect to MySQL server without specifying a database
    connection = MySQLdb.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        port=int(db_port),
    )
    cursor = connection.cursor()

    # Check if the database exists and create it if it doesn't
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        print(f"Database '{db_name}' ensured to exist.")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()
        connection.close()


def run_migrations():
    try:
        # Run makemigrations and migrate
        print("Running makemigrations...")
        call_command('makemigrations')
        print("Running migrate...")
        call_command('migrate')
        print("Migrations completed.")
    except Exception as e:
        print(f"Error during migrations: {e}")


# Run database creation and migrations
create_database_if_not_exists()
# run_migrations()
