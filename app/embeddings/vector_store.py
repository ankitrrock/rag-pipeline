from pathlib import Path

import faiss
import numpy as np


VECTOR_STORE_DIR = Path("data/vector_store")
INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
CHUNK_IDS_PATH = VECTOR_STORE_DIR / "chunk_ids.npy"


class VectorStore:

    def __init__(self, dimension: int = 384):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.chunk_ids: list[int] = []

    def add(
        self,
        embeddings: list[list[float]],
        chunk_ids: list[int],
    ):

        vectors = np.array(
            embeddings,
            dtype="float32",
        )

        self.index.add(vectors)

        self.chunk_ids.extend(chunk_ids)

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ):

        if self.index.ntotal == 0:
            return []

        top_k = min(
            top_k,
            self.index.ntotal,
        )

        vector = np.array(
            [embedding],
            dtype="float32",
        )

        scores, indices = self.index.search(
            vector,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index == -1:
                continue

            results.append(
                {
                    "chunk_id": self.chunk_ids[index],
                    "score": float(score),
                }
            )

        return results

    def save(self):

        VECTOR_STORE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(INDEX_PATH),
        )

        np.save(
            CHUNK_IDS_PATH,
            np.array(
                self.chunk_ids,
                dtype=np.int64,
            ),
        )

        print("FAISS index saved successfully.")

    def load(self):

        if not INDEX_PATH.exists():
            print("No FAISS index found.")
            return False

        if not CHUNK_IDS_PATH.exists():
            print("No chunk ID mapping found.")
            return False

        self.index = faiss.read_index(
            str(INDEX_PATH)
        )

        self.chunk_ids = np.load(
            CHUNK_IDS_PATH
        ).tolist()

        print(
            f"FAISS index loaded. "
            f"Vectors: {self.index.ntotal}"
        )

        return True
    
    def contains_chunk_ids(
        self,
        chunk_ids: list[int],
    ) -> bool:
        existing_ids = set(self.chunk_ids)

        return any(
            chunk_id in existing_ids
            for chunk_id in chunk_ids
    )
        
    def remove_chunk_ids(
        self,
        chunk_ids: list[int],
    ):
        if not chunk_ids:
            return

        chunk_ids_set = set(chunk_ids)

        keep_indices = [
            index
            for index, chunk_id in enumerate(self.chunk_ids)
            if chunk_id not in chunk_ids_set
        ]

        if len(keep_indices) == len(self.chunk_ids):
            return

        if keep_indices:
            vectors = self.index.reconstruct_n(
                0,
                self.index.ntotal,
            )

            vectors = vectors[keep_indices]

            new_index = faiss.IndexFlatIP(
                self.dimension
            )

            new_index.add(
                np.asarray(
                    vectors,
                    dtype="float32",
                )
            )

            self.index = new_index

            self.chunk_ids = [
                self.chunk_ids[index]
                for index in keep_indices
            ]

        else:
            self.index = faiss.IndexFlatIP(
                self.dimension
            )
            self.chunk_ids = []

        self.save()

        print(
            f"Removed {len(chunk_ids_set)} chunk vectors from FAISS."
        )


vector_store = VectorStore()