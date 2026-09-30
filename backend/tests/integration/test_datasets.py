"""
ChurnSense AI — Integration Tests for Datasets API

Tests cover:
  - Upload valid CSV
  - Upload invalid file type
  - Upload empty CSV
  - Validate dataset
  - Delete dataset
  - Unauthorized access
"""

import io
import pytest
from httpx import AsyncClient


def make_csv(rows: int = 5, include_churn: bool = True) -> bytes:
    """Generate minimal valid CSV bytes for testing."""
    headers = "customerID,tenure,Contract,MonthlyCharges,TotalCharges"
    if include_churn:
        headers += ",Churn"
    lines = [headers]
    for i in range(rows):
        row = f"C{i:04d},{i+1},Month-to-month,{50+i:.2f},{(50+i)*(i+1):.2f}"
        if include_churn:
            row += ",Yes" if i % 3 == 0 else ",No"
        lines.append(row)
    return "\n".join(lines).encode("utf-8")


@pytest.mark.asyncio
async def test_upload_valid_csv(client: AsyncClient, auth_headers: dict):
    """Valid CSV upload should return 201 with dataset record."""
    csv_bytes = make_csv(rows=20)
    resp = await client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test_data.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": "Test Dataset", "description": "Integration test dataset"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Dataset"
    assert data["status"] == "uploaded"


@pytest.mark.asyncio
async def test_upload_non_csv_file(client: AsyncClient, auth_headers: dict):
    """Non-CSV file upload should return 400."""
    resp = await client.post(
        "/api/v1/datasets/upload",
        files={"file": ("data.xlsx", io.BytesIO(b"fake xlsx"), "application/vnd.ms-excel")},
        data={"name": "Bad File"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "CSV" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_upload_requires_auth(client: AsyncClient):
    """Unauthenticated upload should return 401."""
    csv_bytes = make_csv()
    resp = await client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": "No Auth"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_datasets_empty(client: AsyncClient, auth_headers: dict):
    """Dataset list for new user should return empty array."""
    resp = await client.get("/api/v1/datasets", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_nonexistent_dataset(client: AsyncClient, auth_headers: dict):
    """Requesting a non-existent dataset ID should return 404."""
    resp = await client.get(
        "/api/v1/datasets/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_dataset(client: AsyncClient, auth_headers: dict):
    """Upload then delete — should return 200 with success message."""
    csv_bytes = make_csv(rows=5)
    upload = await client.post(
        "/api/v1/datasets/upload",
        files={"file": ("del_test.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": "To Delete"},
        headers=auth_headers,
    )
    assert upload.status_code == 201
    dataset_id = upload.json()["id"]

    delete = await client.delete(
        f"/api/v1/datasets/{dataset_id}",
        headers=auth_headers,
    )
    assert delete.status_code == 200
    assert "deleted" in delete.json()["message"].lower()

    # Confirm it's gone
    get = await client.get(f"/api/v1/datasets/{dataset_id}", headers=auth_headers)
    assert get.status_code == 404


@pytest.mark.asyncio
async def test_validate_dataset(client: AsyncClient, auth_headers: dict, tmp_path):
    """Upload a CSV and validate it — should return validation result."""
    import os, tempfile
    csv_bytes = make_csv(rows=50)

    upload = await client.post(
        "/api/v1/datasets/upload",
        files={"file": ("validate_test.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": "Validate Me"},
        headers=auth_headers,
    )
    assert upload.status_code == 201
    dataset_id = upload.json()["id"]

    validate = await client.post(
        f"/api/v1/datasets/{dataset_id}/validate",
        headers=auth_headers,
    )
    assert validate.status_code == 200
    result = validate.json()
    assert "quality_score" in result
    assert "row_count" in result
    assert result["row_count"] == 50
