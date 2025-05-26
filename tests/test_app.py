def test_status(client):
    resp = client.get("/_mgmt/ping")
    assert resp.json() == {"message": "PONG"}


def test_error(client):
    resp = client.get("/does/not/exist")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
