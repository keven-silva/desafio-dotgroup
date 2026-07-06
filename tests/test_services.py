import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.schemas import BookCreate
from app.models.base import Base
from app.services.book_service import BookService
from chatbot.service import PythonDevChatbot
from vector_store.embeddings import EmbeddingGenerator
from vector_store.service import VectorStoreService


class ServicesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.db = Session(bind=self.engine)

    def tearDown(self) -> None:
        self.db.close()

    def test_book_service_create_and_get(self) -> None:
        service = BookService(self.db)
        created = service.create(BookCreate(title="Clean Code", author="Robert Martin"))

        fetched = service.get(created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual("Clean Code", fetched.title)

    def test_chatbot_answer_python_topic(self) -> None:
        bot = PythonDevChatbot()
        answer = bot.answer("Quais boas práticas com FastAPI?")
        self.assertIn("routers", answer.lower())

    def test_vector_store_ingest(self) -> None:
        service = VectorStoreService(self.db, generator=EmbeddingGenerator(dimensions=8))
        stored = service.ingest(
            source="https://blog.exemplo.com/post",
            content="Post sobre boas práticas em desenvolvimento Python.",
        )
        self.assertEqual(8, len(stored.embedding))
        self.assertEqual("https://blog.exemplo.com/post", stored.source)


if __name__ == "__main__":
    unittest.main()
