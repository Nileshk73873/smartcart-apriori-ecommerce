"""
Integration tests for backend authentication, admin protection, and cart isolation.
Uses FastAPI TestClient and SQLite in-memory or test database session.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db
from backend.models import User, Product
from backend.auth import hash_password, create_access_token
from backend.cart import USER_CARTS

# Create clean in-memory test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine_test)
    USER_CARTS.clear()
    yield
    Base.metadata.drop_all(bind=engine_test)
    USER_CARTS.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_signup_cannot_create_admin(client):
    """Ensure signup always sets is_admin=False even if attempted."""
    res = client.post(
        "/api/auth/signup",
        json={"username": "malicious_user", "email": "user@test.com", "password": "password123", "is_admin": True}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_admin"] is False

    # Check directly in database
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "malicious_user").first()
    assert user is not None
    assert user.is_admin is False
    db.close()


def test_admin_routes_protected_against_unauthenticated(client):
    """Admin routes return 401 when no token is provided."""
    res = client.get("/api/admin/users")
    assert res.status_code == 401


def test_admin_routes_protected_against_non_admin_token(client):
    """Admin routes return 403 when a non-admin user token is provided."""
    db = TestingSessionLocal()
    user = User(username="regular_user", password=hash_password("pass123"), is_admin=False)
    db.add(user)
    db.commit()
    db.close()

    token = create_access_token({"sub": "regular_user"})
    res = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]


def test_admin_routes_accessible_with_admin_token(client):
    """Admin routes return 200 with an admin token."""
    db = TestingSessionLocal()
    admin_user = User(username="admin_user", password=hash_password("pass123"), is_admin=True)
    db.add(admin_user)
    db.commit()
    db.close()

    token = create_access_token({"sub": "admin_user"})
    res = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_carts_are_isolated_per_user(client):
    """Adding products to User 1's cart does not affect User 2's cart or a guest's cart."""
    db = TestingSessionLocal()
    u1 = User(username="user1", password=hash_password("pass1"), is_admin=False)
    u2 = User(username="user2", password=hash_password("pass2"), is_admin=False)
    p1 = Product(stock_code="P1", name="Product One", price=10.0)
    p2 = Product(stock_code="P2", name="Product Two", price=20.0)
    db.add_all([u1, u2, p1, p2])
    db.commit()
    p1_id = p1.id
    p2_id = p2.id
    db.close()

    token1 = create_access_token({"sub": "user1"})
    token2 = create_access_token({"sub": "user2"})

    # User 1 adds Product 1
    client.post(
        "/api/cart/add",
        json={"product_id": p1_id, "quantity": 2},
        headers={"Authorization": f"Bearer {token1}"}
    )

    # User 2 adds Product 2
    client.post(
        "/api/cart/add",
        json={"product_id": p2_id, "quantity": 5},
        headers={"Authorization": f"Bearer {token2}"}
    )

    # Guest adds Product 1 with guest session header
    client.post(
        "/api/cart/add",
        json={"product_id": p1_id, "quantity": 1},
        headers={"X-Session-ID": "guest_session_123"}
    )

    # Verify User 1's cart has 2 of P1 only
    cart1 = client.get("/api/cart/", headers={"Authorization": f"Bearer {token1}"}).json()
    assert len(cart1["items"]) == 1
    assert cart1["items"][0]["product"]["id"] == p1_id
    assert cart1["items"][0]["quantity"] == 2

    # Verify User 2's cart has 5 of P2 only
    cart2 = client.get("/api/cart/", headers={"Authorization": f"Bearer {token2}"}).json()
    assert len(cart2["items"]) == 1
    assert cart2["items"][0]["product"]["id"] == p2_id
    assert cart2["items"][0]["quantity"] == 5

    # Verify Guest's cart has 1 of P1 only
    cart_guest = client.get("/api/cart/", headers={"X-Session-ID": "guest_session_123"}).json()
    assert len(cart_guest["items"]) == 1
    assert cart_guest["items"][0]["product"]["id"] == p1_id
    assert cart_guest["items"][0]["quantity"] == 1
