from fastapi import APIRouter

from app.services.chroma_service import (
    semantic_search
)

router = APIRouter()


@router.get("/semantic-search")

async def semantic_search_api(
    query: str
):

    results = semantic_search(query)

    return {

        "success": True,

        "query": query,

        "results": results
    }

# from fastapi import APIRouter

# from app.services.chroma_service import (
#     semantic_search
# )

# router = APIRouter()


# @router.get("/semantic-search")

# async def semantic_search_api(
#     query: str
# ):

#     results = semantic_search(query)

#     formatted_results = []

#     documents = results["documents"][0]
#     metadatas = results["metadatas"][0]
#     distances = results["distances"][0]

#     for i in range(len(documents)):

#         formatted_results.append({

#             "name":
#                 metadatas[i]["name"],

#             "type":
#                 metadatas[i]["type"],

#             "document":
#                 documents[i],

#             "similarity_score":
#                 round(
#                     1 - distances[i],
#                     3
#                 )
#         })

#     return {

#         "success": True,

#         "query": query,

#         "results": formatted_results
#     }