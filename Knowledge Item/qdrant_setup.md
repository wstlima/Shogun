# Qdrant Vector Store Setup — Embedded Mode & Memory Integration

## Overview

Shogun uses **Qdrant** as its vector database for semantic memory search. The system supports two deployment modes:

| Mode | Config | Use Case |
|------|--------|----------|
| **Embedded** (default) | `qdrant_path = data/qdrant/` | Zero-dependency local development. Qdrant runs in-process via `qdrant-client`. |
| **Remote** | `QDRANT_URL=http://localhost:6333` | Production/multi-process. Qdrant runs as a container. |

---

## Configuration

### Settings (`shogun/config.py`)

```python
class Settings(BaseSettings):
    qdrant_url: str | None = None          # If set → remote mode
    qdrant_path: Path = PROJECT_ROOT / "data" / "qdrant"  # Embedded storage path
```

- **Embedded mode** (default): `qdrant_url` is `None`, client uses `QdrantClient(path=str(settings.qdrant_path))`.
- **Remote mode**: Set `QDRANT_URL` env var, client uses `QdrantClient(url=settings.qdrant_url)`.

### Docker Compose (`docker-compose.yml`)

For remote mode, Qdrant runs as a container:

```yaml
qdrant:
  image: qdrant/qdrant:v1.12.5
  container_name: shogun-qdrant
  ports:
    - "6333:6333"   # REST API
    - "6334:6334"   # gRPC
  volumes:
    - shogun_qdrant_data:/qdrant/storage
```

### Directory Creation

`settings.ensure_directories()` (called during bootstrap) creates `data/qdrant/` automatically.

---

## Embedding Model

| Property | Value |
|----------|-------|
| **Model** | `BAAI/bge-small-en-v1.5` |
| **Dimensions** | 384 |
| **Library** | `sentence-transformers` |
| **Normalization** | Enabled (`normalize_embeddings=True`) |
| **Batch size** | 32 |

The embedder is **lazy-loaded** on first use (not at import time) to avoid slow startup when Qdrant isn't needed.

---

## Collection: `shogun_memories`

### Schema

```python
VectorParams(size=384, distance=Distance.COSINE)
```

- **Single collection** for all memory types.
- **Score threshold**: `0.15` (filters out very low similarity results).

### Payload Fields

Each Qdrant point carries a payload with filterable metadata:

| Field | Type | Description |
|-------|------|-------------|
| `memory_id` | `str` | UUID of the MemoryRecord in SQLite |
| `memory_type` | `str` | One of: `episodic`, `semantic`, `procedural`, `persona`, `skills` |
| `agent_id` | `str` | UUID of the owning agent |
| `title` | `str` | Memory title |
| `importance_score` | `float` | Intrinsic importance (0–1) |
| `decay_class` | `str` | One of: `fast`, `medium`, `slow`, `sticky`, `pinned` |
| `is_pinned` | `bool` | Whether the memory is pinned (no decay) |
| `tags` | `list[str]` | User-assigned tags |
| `content_preview` | `str` | First 500 chars of content |

---

## VectorStore Class (`shogun/engine/vector_store.py`)

### Singleton Access

```python
from shogun.engine.vector_store import get_vector_store

store = get_vector_store()  # always returns the same instance
```

### Key Methods

#### `ensure_collection()`
Creates the `shogun_memories` collection if it doesn't exist. Called during bootstrap.

#### `embed(text: str) → list[float]`
Embeds a single text string into a 384-dimensional normalized float vector.

#### `embed_batch(texts: list[str]) → list[list[float]]`
Batch embedding with batch size of 32.

#### `upsert(memory_id, text, payload)`
Embeds text and upserts a single point into Qdrant. Adds `memory_id` and `content_preview` to payload automatically.

#### `upsert_batch(items: list[dict]) → int`
Batch upsert. Each item must have `id`, `text`, and optional `payload`. Returns count of points inserted.

#### `search(query_text, *, memory_types, agent_id, min_importance, pinned_only, limit) → list[dict]`
Semantic search with optional payload filters. Uses `query_points` API. Returns list of `{memory_id, score, payload}`.

**Filter logic**:
- Multiple `memory_types` → Qdrant `should` filter (OR)
- Single `memory_type` + other filters → Qdrant `must` filter (AND)
- `min_importance` → `Range(gte=value)` filter
- `pinned_only` → `MatchValue(value=True)` filter

#### `delete_point(memory_id)`
Removes a vector point. Called when a memory is archived/forgotten.

#### `drop_and_recreate()`
Drops and recreates the collection. Used for full reindex operations.

#### `collection_info() → dict`
Returns collection status including point count. Handles the lock error gracefully when another process holds the embedded DB.

---

## Integration with MemoryService

The `MemoryService` (`shogun/services/memory_service.py`) is the primary consumer of the VectorStore. Every memory operation is **dual-written**:

### Create Flow

```
MemoryService.create_memory()
  ├─ 1. SQLite INSERT (via BaseService.create)
  ├─ 2. Build embed text: "{title}\n\n{summary}\n\n{content}"
  ├─ 3. VectorStore.upsert(memory_id, embed_text, payload)
  └─ 4. Store qdrant_point_id on the MemoryRecord
```

### Search Flow (Hybrid)

```
MemoryService.search(query)
  ├─ 1. VectorStore.search() → top-N candidates (over-fetched at 2×limit)
  ├─ 2. Fetch full metadata from SQLite for hit IDs
  ├─ 3. Compute live salience scores:
  │     ├─ Decayed relevance (time-based decay by decay_class)
  │     └─ Recency boost (based on last_accessed_at)
  ├─ 4. Rerank via salience engine:
  │     ├─ semantic_similarity: 50%
  │     ├─ relevance_score: 20%
  │     ├─ importance_score: 15%
  │     ├─ recency_boost: 10%
  │     └─ confidence_score: 5%
  └─ 5. Return top-N with full score breakdown
```

> The Qdrant search runs in a thread pool (`asyncio.to_thread()`) to avoid blocking the event loop.

### Forget Flow

```
MemoryService.forget_memory(memory_id)
  ├─ 1. Set is_archived=True in SQLite
  └─ 2. VectorStore.delete_point(memory_id)
```

### Reindex Flow

```
MemoryService.reindex_all()
  ├─ 1. VectorStore.drop_and_recreate()
  ├─ 2. Fetch all active memories from SQLite
  ├─ 3. VectorStore.upsert_batch(all_items)
  └─ 4. Update qdrant_point_ids on all records
```

---

## Bootstrap Initialization

During `bootstrap.py`:

```python
async def _init_qdrant():
    store = get_vector_store()
    store.ensure_collection()

async def _seed_memories():
    # Inserts 8 seed memories into both SQLite and Qdrant
    store.upsert_batch(items)
```

Bootstrap also seeds 8 example memories (persona, procedural, semantic, episodic, skills types) so the Archives page isn't empty on first run.

---

## Known Gotchas

1. **Lock error in embedded mode**: If another process (e.g., a second Shogun instance) holds the embedded Qdrant DB, you get `"already accessed by another instance"`. The `collection_info()` method handles this gracefully by returning `status: "active (locked)"`.

2. **Lazy loading**: Both the Qdrant client and the SentenceTransformer model are lazy-loaded on first access. First search will be slow (~2–5 seconds for model load).

3. **Point IDs are UUIDs as strings**: Qdrant point IDs are the string representation of SQLite MemoryRecord UUIDs. They must match exactly for delete/update operations.

4. **Over-fetching**: The search flow over-fetches at `limit * 2` from Qdrant to give the salience reranker more candidates to work with, then returns the top `limit`.
