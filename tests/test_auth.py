import pytest
from httpx import AsyncClient, ASGITransport
import uuid
import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Import your FastAPI app and database dependencies
from server import app
from db import get_session
from auth.models import User

# --- Setup Test Database ---
# Create an in-memory SQLite database for testing
DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    DATABASE_URL_TEST,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

async def get_test_session() -> AsyncSession:
    async with AsyncSession(engine_test) as session:
        yield session

# Override the database dependency in the app
app.dependency_overrides[get_session] = get_test_session


@pytest.fixture(autouse=True, scope="function")
async def setup_db():
    # Create the tables in the test database before each test
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Drop the tables after each test
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# --- Tests ---

@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hased_password" not in data # Ensure password is not returned


@pytest.mark.asyncio
async def test_register_user_duplicate_email(async_client: AsyncClient):
    # Register first time
    await async_client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"},
    )
    
    # Try registering again with the same email
    response = await async_client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "newpassword456"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "email already exsisted"}


@pytest.mark.asyncio
async def test_login_user_success(async_client: AsyncClient):
    # Setup: Create a user
    await async_client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "securepassword"},
    )

    # Test login
    response = await async_client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "securepassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login@example.com"


@pytest.mark.asyncio
async def test_login_user_invalid_credentials(async_client: AsyncClient):
    # Setup: Create a user
    await async_client.post(
        "/auth/register",
        json={"email": "wrongpass@example.com", "password": "rightpassword"},
    )

    # Test login with wrong password
    response = await async_client.post(
        "/auth/login",
        data={"username": "wrongpass@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

    # Test login with non-existent user
    response_no_user = await async_client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "password123"},
    )
    assert response_no_user.status_code == 401
    assert response_no_user.json() == {"detail": "Invalid credentials"}
