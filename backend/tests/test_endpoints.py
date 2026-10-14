def test_root_endpoint(client):
    """Test root greeting endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Acadexa AI" in data["message"]


def test_health_check(client):
    """Test health check returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_test_connectivity(client):
    """Test frontend/backend connectivity verification route."""
    response = client.get("/api/test")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "FastAPI" in data["message"]


def test_register_user_success(client):
    """Test registering a new user with valid credentials."""
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane@example.com"
    assert data["name"] == "Jane Doe"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_email(client, test_user):
    """Test registering with an existing email returns 400 Bad Request."""
    payload = {
        "name": "Duplicate User",
        "email": test_user.email,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "Email already registered" in data["detail"]
    assert data["error_code"] == "BAD_REQUEST"


def test_register_validation_error_short_password(client):
    """Test user registration input validation on password length."""
    payload = {
        "name": "Short Pwd",
        "email": "short@example.com",
        "password": "short",  # Less than 8 characters
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "password" in data["detail"].lower()


def test_login_user_success(client, test_user):
    """Test authenticating a user with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_invalid_credentials(client, test_user):
    """Test login failure with incorrect password returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword999",
        },
    )
    assert response.status_code == 401
    data = response.json()
    assert "Invalid email or password" in data["detail"]
    assert data["error_code"] == "UNAUTHORIZED"


def test_get_current_user_authenticated(client, auth_headers, test_user):
    """Test retrieving authenticated user profile."""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


def test_get_current_user_unauthorized(client):
    """Test accessing protected user endpoint without token returns 401."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_update_user_profile(client, auth_headers):
    """Test updating user profile details."""
    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_get_user_dashboard(client, auth_headers):
    """Test fetching user dashboard stats."""
    response = client.get("/api/v1/users/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "total_documents" in data["stats"]
    assert "recent_uploads" in data


def test_notes_crud_lifecycle(client, auth_headers):
    """Test full CRUD lifecycle for notes: create, list, retrieve, update, delete."""
    # 1. Create note
    create_payload = {
        "title": "Algorithms Lecture 1",
        "content": "Graph traversal using BFS and DFS.",
        "subject": "Computer Science",
    }
    create_res = client.post("/api/v1/notes", headers=auth_headers, json=create_payload)
    assert create_res.status_code == 201
    note = create_res.json()
    note_id = note["id"]
    assert note["title"] == create_payload["title"]

    # 2. List notes
    list_res = client.get("/api/v1/notes", headers=auth_headers)
    assert list_res.status_code == 200
    notes_list = list_res.json()
    assert len(notes_list) >= 1
    assert any(n["id"] == note_id for n in notes_list)

    # 3. Retrieve single note
    get_res = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == create_payload["title"]

    # 4. Update note
    update_res = client.put(
        f"/api/v1/notes/{note_id}",
        headers=auth_headers,
        json={"title": "Algorithms - Updated", "content": "Updated content with Dijkstra"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Algorithms - Updated"

    # 5. Delete note
    del_res = client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 6. Verify note is deleted
    not_found_res = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert not_found_res.status_code == 404
    assert not_found_res.json()["error_code"] == "NOT_FOUND"


def test_note_validation_empty_title(client, auth_headers):
    """Test that creating a note with blank title fails validation."""
    response = client.post(
        "/api/v1/notes",
        headers=auth_headers,
        json={"title": "   ", "content": "Some content"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"


def test_list_documents(client, auth_headers):
    """Test retrieving documents list for an authenticated user."""
    response = client.get("/api/v1/documents", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_documents_validation(client, auth_headers):
    """Test search endpoint validation when query parameter 'q' is missing."""
    response = client.get("/api/v1/documents/search", headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"
