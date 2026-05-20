import chromadb

from sentence_transformers import (
    SentenceTransformer
)

from app.services.sqlite_service import (
    get_all_services
)

from app.services.embedding_prep_service import (
    build_service_text
)

from app.services.ai_scoring_service import (
    calculate_emergency_score
)

# CHROMA CLIENT

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="emergency_services"
)

# EMBEDDING MODEL

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def generate_embeddings():

    services = get_all_services()

    for service in services:

        text = build_service_text(service)

        embedding = model.encode(text).tolist()

        collection.add(

            ids=[str(service["id"])],

            embeddings=[embedding],

            documents=[text],

            metadatas=[

                {
                    "name": service["name"],
                    "type": service["type"]
                }
            ]
        )

    print("Embeddings stored successfully.")


def semantic_search(query: str):

    query_embedding = (
        model.encode(query).tolist()
    )

    results = collection.query(

        query_embeddings=[query_embedding],

        n_results=5
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    services = get_all_services()

    formatted_results = []

    for i in range(len(documents)):

        service_id = int(ids[i])

        matched_service = next(

            (
                s for s in services
                if s["id"] == service_id
            ),

            None
        )

        if not matched_service:
            continue

        semantic_score = round(
            1 / (1 + distances[i]),
            3
        )

        emergency_score = (
            calculate_emergency_score(
                matched_service
            )
        )

        final_score = round(

            (
                semantic_score * 0.4
                +
                emergency_score * 0.6
            ),

            3
        )

        formatted_results.append({

            "name":
                matched_service["name"],

            "type":
                matched_service["type"],

            "semantic_score":
                semantic_score,

            "emergency_score":
                emergency_score,

            "final_score":
                final_score
        })

    formatted_results.sort(

        key=lambda x: x["final_score"],

        reverse=True
    )

    return formatted_results