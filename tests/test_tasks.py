def register_and_login(client, email, name):
    client.post("/auth/register", json={"email": email, "password": "secret123", "name": name})
    response = client.post("/auth/login", json={"email": email, "password": "secret123"})
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_update_task_status(client):
    manager_token = register_and_login(client, "status_manager@example.com", "Manager")
    employee_token = register_and_login(client, "status_employee@example.com", "Employee")
    outsider_token = register_and_login(client, "status_outsider@example.com", "Outsider")

    team_resp = client.post("/teams/", json={"name": "Status Team"}, headers=auth_headers(manager_token))
    assert team_resp.status_code == 200
    team = team_resp.json()
    team_id = team["id"]
    invite_code = team["invite_code"]

    client.post(f"/teams/{team_id}/join", json={"invite_code": invite_code}, headers=auth_headers(employee_token))
    client.post(f"/teams/{team_id}/join", json={"invite_code": invite_code}, headers=auth_headers(outsider_token))

    employee_id = client.get("/users/me", headers=auth_headers(employee_token)).json()["id"]

    task_resp = client.post(
        f"/teams/{team_id}/tasks",
        json={"title": "Test task", "due_date": "2026-09-01T00:00:00", "assignee_id": employee_id},
        headers=auth_headers(manager_token),
    )
    assert task_resp.status_code == 200
    task_id = task_resp.json()["id"]


    r1 = client.patch(
        f"/teams/{team_id}/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=auth_headers(employee_token),
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "in_progress"

    r2 = client.patch(
        f"/teams/{team_id}/tasks/{task_id}/status",
        json={"status": "done"},
        headers=auth_headers(manager_token),
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "done"

    r3 = client.patch(
        f"/teams/{team_id}/tasks/{task_id}/status",
        json={"status": "open"},
        headers=auth_headers(outsider_token),
    )
    assert r3.status_code == 403

    r4 = client.patch(
        f"/teams/{team_id}/tasks/999999/status",
        json={"status": "open"},
        headers=auth_headers(manager_token),
    )
    assert r4.status_code == 404
