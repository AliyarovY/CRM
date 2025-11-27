import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from app.main import app
from app.database import get_db, Base
from app.models import User, Organization, OrganizationMember
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.core.permissions import Role


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield engine

    await engine.dispose()
    app.dependency_overrides.clear()


@pytest.fixture
async def client(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_organization(test_db):
    async with AsyncSession(test_db, expire_on_commit=False) as session:
        org = Organization(
            id=uuid4(),
            name="Test Organization",
            is_active=True,
        )
        session.add(org)
        await session.commit()
        await session.refresh(org)
        yield org


@pytest.fixture
async def test_user(test_db, test_organization):
    async with AsyncSession(test_db, expire_on_commit=False) as session:
        user = User(
            id=uuid4(),
            email="testuser@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password_hash=hash_password("testpassword123"),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        org_member = OrganizationMember(
            id=uuid4(),
            user_id=user.id,
            organization_id=test_organization.id,
            role=Role.OWNER,
            is_active=True,
        )
        session.add(org_member)
        await session.commit()

        yield user


@pytest.fixture
async def test_user_token(test_user):
    access_token = create_access_token({"sub": str(test_user.id)})
    refresh_token = create_refresh_token({"sub": str(test_user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@pytest.fixture
async def test_user_sales(test_db, test_organization):
    async with AsyncSession(test_db, expire_on_commit=False) as session:
        user = User(
            id=uuid4(),
            email="sales@example.com",
            username="sales_user",
            first_name="Sales",
            last_name="User",
            password_hash=hash_password("salespassword123"),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        org_member = OrganizationMember(
            id=uuid4(),
            user_id=user.id,
            organization_id=test_organization.id,
            role=Role.SALES,
            is_active=True,
        )
        session.add(org_member)
        await session.commit()

        yield user


@pytest.fixture
async def test_user_sales_token(test_user_sales):
    access_token = create_access_token({"sub": str(test_user_sales.id)})
    refresh_token = create_refresh_token({"sub": str(test_user_sales.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@pytest.fixture
async def auth_headers(test_user_token, test_organization):
    return {
        "Authorization": f"Bearer {test_user_token['access_token']}",
        "X-Organization-Id": str(test_organization.id),
    }


@pytest.fixture
async def sales_auth_headers(test_user_sales_token, test_organization):
    return {
        "Authorization": f"Bearer {test_user_sales_token['access_token']}",
        "X-Organization-Id": str(test_organization.id),
    }
