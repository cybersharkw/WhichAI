from fastapi.testclient import TestClient

from backend.main import create_app

CASE = {
    "name": "Refund question",
    "input": "  Please refund my order.\n",
    "reference_answer": "billing",
    "evaluation_criteria": ["Correct category", "No invented facts"],
}


def test_create_and_read_dataset(client):
    response = client.post("/datasets", json={"name": " Support "})
    assert response.status_code == 201
    dataset = response.json()
    assert dataset["name"] == "Support"
    assert dataset["description"] == ""
    assert dataset["created_at"]
    assert client.get(f"/datasets/{dataset['id']}").json() == dataset
    assert client.get("/datasets").json() == [dataset]
    assert client.get("/datasets?offset=1&limit=1").json() == []


def test_cases_belong_to_the_correct_dataset(client):
    first = client.post("/datasets", json={"name": "First"}).json()["id"]
    second = client.post("/datasets", json={"name": "Second"}).json()["id"]
    response = client.post(f"/datasets/{first}/cases", json=CASE)
    assert response.status_code == 201
    case = response.json()
    assert case["dataset_id"] == first
    assert case["input"] == CASE["input"]  # Preserve prompt formatting.
    assert case["evaluation_criteria"] == CASE["evaluation_criteria"]
    assert client.get(f"/datasets/{first}/cases").json() == [case]
    assert client.get(f"/datasets/{first}/cases?offset=1").json() == []
    assert client.get(f"/datasets/{second}/cases").json() == []


def test_missing_dataset_returns_404(client):
    assert client.get("/datasets/999").status_code == 404
    assert client.get("/datasets/999/cases").status_code == 404
    response = client.post("/datasets/999/cases", json=CASE)
    assert response.status_code == 404
    assert response.json() == {"detail": "Dataset 999 not found"}


def test_invalid_input_does_not_write_records(client):
    assert client.post("/datasets", json={"name": "   "}).status_code == 422
    assert client.post("/datasets", json={"name": "x", "id": 1}).status_code == 422
    assert client.get("/datasets").json() == []
    dataset_id = client.post("/datasets", json={"name": "Valid"}).json()["id"]
    for patch in ({"input": "  "}, {"reference_answer": ""}, {"evaluation_criteria": [" "]}):
        response = client.post(f"/datasets/{dataset_id}/cases", json={**CASE, **patch})
        assert response.status_code == 422
    assert client.get(f"/datasets/{dataset_id}/cases").json() == []
    assert client.get("/datasets?limit=101").status_code == 422
    assert client.get("/datasets?offset=-1").status_code == 422


def test_data_survives_application_restart(database_settings):
    with TestClient(create_app(database_settings)) as first_client:
        dataset = first_client.post("/datasets", json={"name": "Persistent"}).json()
        case = first_client.post(f"/datasets/{dataset['id']}/cases", json=CASE).json()

    # A new application and engine must read the same on-disk database.
    with TestClient(create_app(database_settings)) as second_client:
        assert second_client.get(f"/datasets/{dataset['id']}").json() == dataset
        assert second_client.get(f"/datasets/{dataset['id']}/cases").json() == [case]


def test_existing_routes_still_work(client):
    assert client.get("/").json() == {"message": "Hello World"}
    assert client.get("/health").json() == {"status": "ok"}
    config = {
        "name": "Example model", "type": "chat", "version": 1.0,
        "systemPrompt": "Be helpful", "checkpoint": False, "rag": False,
        "agent": False, "toolItems": [],
    }
    assert client.post("/generations", json=config).json() == config


def test_service_can_be_replaced_with_dependency_override(client):
    from backend.api.dependencies import get_dataset_service

    class FakeDatasetService:
        def list_datasets(self, *, offset, limit):
            return []

    # No endpoint changes are needed to inject a different service.
    client.app.dependency_overrides[get_dataset_service] = lambda: FakeDatasetService()
    try:
        assert client.get("/datasets").json() == []
    finally:
        client.app.dependency_overrides.clear()
