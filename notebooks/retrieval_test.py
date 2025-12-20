# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %%
"""
Query the collection using Chroma's built-in embedding function

This script follows https://docs.trychroma.com/docs/querying-collections/query-and-get by simply passing `query_texts` to `.query`; Chroma handles embedding for you, so there is no need to instantiate `OpenAIEmbeddingFunction` or otherwise precompute embeddings before calling the query.
"""

# %%
from pprint import pprint

import chromadb
from chromadb.errors import InvalidArgumentError

from src.utils.chroma_utils import repor

# %%
client = chromadb.HttpClient(host="localhost", port=8000)
collection_count = client.count_collections()
print("Available collections:", collection_count)



collections = client.list_collections()
collection_names = [collection.name for collection in collections]
print("Found collections:", collection_names)

# %% [markdown]
# ## create some test dbs

# %%
# Set your OPENAI_API_KEY environment variable
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

collection = client.get_or_create_collection(
    name="my_collection_small",
    embedding_function=OpenAIEmbeddingFunction(
        model_name="text-embedding-3-small"
    )
)

# Chroma will use OpenAIEmbeddingFunction to embed your documents
collection.add(
    ids=["id1", "id2"],
    documents=["doc1 hi  ", "doc2 hi"]
)

collection.query(query_texts=["doc1"], n_results=1)



# %%
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

fn_lg = OpenAIEmbeddingFunction(
        model_name="text-embedding-3-large"
    )

collection = client.get_or_create_collection(
    name="my_collection_large",
    embedding_function=fn_lg
)

# Chroma will use OpenAIEmbeddingFunction to embed your documents
collection.add(
    ids=["id1", "id2"],
    documents=["doc1 hello", "doc2 hello"]
)

collection.query(query_texts=["doc1"], n_results=1)



# %%

# preview
preview = fn_lg(["hello world", "hi there"])
print(type(preview))
print(len(preview))
print(len(preview[0]))

# %%
vars(collection)

# %%
collection_name = collection_names[0] if collection_names else "cards-v1__openai__text-embedding-3-small__v1"
print("Using collection:", collection_name)

collection = client.get_collection(name=collection_name)

# %%
collection.query(query_texts=["What is a cue card?"], n_results=2)

# %%
fn = collection._embedding_function
fn

# %%

# %%
collection.query(query_texts=["doc1"], n_results=2)


# %%
collection

# %%
query_text = "Tell me about the bobbit worm card."
results = collection.query(
    query_texts=[query_text],
    n_results=5,
    include=["documents", "metadatas", "distances"],
)

pprint(results)

# %%
documents = results.get("documents") or [[]]
metadatas = results.get("metadatas") or [[]]
distances = results.get("distances") or [[]]
ids = results.get("ids") or [[]]

for rank, (doc, meta, dist, doc_id) in enumerate(zip(documents, metadatas, distances, ids), start=1):
    print(
        f"Result {rank} (id={doc_id}, distance={dist:.4f}):\n"
        f"{doc}\n"
        f"Metadata: {meta}\n"
    )

# %%
client = chromadb.HttpClient(host="localhost", port=8000)

# %%

# %%
