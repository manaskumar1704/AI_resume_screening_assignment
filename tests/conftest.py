import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from io import BytesIO
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db


class InMemoryDB:
    def __init__(self):
        self.evaluations = {}

    async def add(self, evaluation):
        self.evaluations[str(evaluation.id)] = evaluation

    async def commit(self):
        pass

    async def refresh(self, evaluation):
        pass


@pytest_asyncio.fixture
async def test_db_session():
    mem_db = InMemoryDB()

    class MockSession:
        def __init__(self, db):
            self.db = db

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def add(self, evaluation):
            await self.db.add(evaluation)

        async def commit(self):
            await self.db.commit()

        async def refresh(self, evaluation):
            await self.db.refresh(evaluation)

        async def execute(self, query):
            return self

        def scalar_one_or_none(self):
            return None

    session = MockSession(mem_db)

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield session
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_resume_pdf():
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Resources<</Font<</F1 4 0 R>>>/Parent 2 0 R/Contents 5 0 R>>endobj 4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj 5 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (John Doe - Software Engineer) Tj ET
endstream endobj xref 0 6 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000100 00000 n 0000000153 00000 n 0000000219 00000 n trailer<</Size 6/Root 1 0 R>> startxref 298 %%EOF"""
    return BytesIO(pdf_content)
