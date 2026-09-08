from app.db.session import engine, Base
from app.db.models import User, Doctor, Appointment

def init_db():
    """
    Initializes the database by creating all tables defined in the models.
    """
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
