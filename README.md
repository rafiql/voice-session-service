# Voice Session Service

A FastAPI microservice for managing voice call sessions with PostgreSQL backend.

---

## **Setup Instructions**

### 1. Clone the repository
```bash
git clone https://github.com/rafiql/voice-session-service.git
cd voice-session-service

2. Install Python and create virtual environment

python3 --version
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

3. Install PostgreSQL
sudo apt install postgresql postgresql-contrib

4. Setup database
sudo -u postgres psql
CREATE DATABASE voice_sessions;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE voice_sessions TO postgres;
\q

5. Install Alembic
pip install alembic
Edit alembic.ini:
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/voice_sessions
Edit env.py to point to your SQLAlchemy Base metadata:
from app.db.database import Base
target_metadata = Base.metadata

alembic revision --autogenerate -m "create call_sessions table"
alembic upgrade head

6. Create a .env file in the root folder
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/voice_sessions

7. Run the FastAPI app
uvicorn app.main:app --reload
Access http://127.0.0.1:8000/docs

8. Run tests
pytest -v tests/test_service.py
