import openai
from qdrant_client.qdrant_client import QdrantClient

from config import OPENAI_API_KEY, QDRANT_API_KEY


class SimilaritySearcher:
    def __init__(self) -> None:
        self.qdrant_client = QdrantClient(
            url=QDRANT_API_KEY,
            api_key=QDRANT_API_KEY,
        )
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY)

    def similarity_search(self, text):
        embeddings = (
            self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text,
            )
            .data[0]
            .embedding
        )
        results = self.qdrant_client.search(
            collection_name="winter_sports",
            query_vector=embeddings,
            limit=5,
        )

        return results


similarity_searcher = SimilaritySearcher()


def get_similarity_searcher():
    return similarity_searcher
