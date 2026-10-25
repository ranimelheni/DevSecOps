def register_and_login(client, email="a@example.com", password="Sup3rSecret!"):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_duplicate_registration_rejected(client):
    register_and_login(client)
    r = client.post("/auth/register", json={"email": "a@example.com", "password": "Sup3rSecret!"})
    assert r.status_code == 409


def test_short_password_rejected(client):
    r = client.post("/auth/register", json={"email": "a@example.com", "password": "short"})
    assert r.status_code == 422


def test_wrong_password_rejected(client):
    register_and_login(client)
    r = client.post("/auth/login", data={"username": "a@example.com", "password": "nope-nope-nope"})
    assert r.status_code == 401


def test_notes_require_auth(client):
    assert client.get("/notes").status_code == 401


def test_note_crud(client):
    h = register_and_login(client)
    r = client.post("/notes", json={"title": "First", "content": "hello"}, headers=h)
    assert r.status_code == 201
    note_id = r.json()["id"]
    assert client.get("/notes", headers=h).json()[0]["title"] == "First"
    assert client.get(f"/notes/{note_id}", headers=h).status_code == 200
    assert client.delete(f"/notes/{note_id}", headers=h).status_code == 204
    assert client.get(f"/notes/{note_id}", headers=h).status_code == 404


