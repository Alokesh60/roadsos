from app.services.sqlite_service import get_all_services

from app.services.embedding_prep_service import (
    build_service_text
)

from app.services.chroma_service import (
    generate_embeddings
)

generate_embeddings()

services = get_all_services()

for service in services:

    print(
        build_service_text(service)
    )