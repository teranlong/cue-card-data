from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.utils.chroma_utils import build_embedding_function
from src.utils.collections import build_collection_name


@dataclass(slots=True)
class CollectionConfig:
    """Configuration for a single Chroma collection."""

    source_path: Path
    provider: str
    embedding_model: str
    variant: str | None = None
    batch_size: int = 200
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any], base_dir: Path) -> "CollectionConfig":
        if "source_path" not in raw:
            raise ValueError("Collection config requires a 'source_path'.")

        source_path = Path(raw["source_path"])
        if not source_path.is_absolute():
            source_path = (base_dir / source_path).resolve()

        provider_raw = raw.get("provider")
        embedding_model_raw = raw.get("embedding_model")
        if not provider_raw or not str(provider_raw).strip():
            raise ValueError("Collection config requires a 'provider'.")
        if not embedding_model_raw or not str(embedding_model_raw).strip():
            raise ValueError("Collection config requires an 'embedding_model'.")

        provider = str(provider_raw).strip()
        embedding_model = str(embedding_model_raw).strip()
        variant = raw.get("variant")
        name = raw.get("name")
        batch_size = int(raw.get("batch_size") or 200)
        metadata = raw.get("metadata") or {}

        if not isinstance(metadata, dict):
            raise ValueError("Collection metadata must be a JSON object.")
        if batch_size <= 0:
            raise ValueError("batch_size must be positive.")

        return cls(
            source_path=source_path,
            provider=provider,
            embedding_model=embedding_model,
            variant=variant,
            batch_size=batch_size,
            name=name,
            metadata=metadata,
        )

    @property
    def collection_name(self) -> str:
        """Return the configured or derived collection name."""

        if self.name:
            return self.name

        return build_collection_name(
            source_path=self.source_path,
            provider=self.provider,
            embedding_model=self.embedding_model,
            variant=self.variant,
        )

    @property
    def collection_metadata(self) -> dict[str, Any]:
        """Build metadata payload attached to the Chroma collection."""

        metadata = {
            "source": str(self.source_path),
            "provider": self.provider,
            "embedding_model": self.embedding_model,
        }
        if self.variant:
            metadata["variant"] = self.variant
        metadata.update(self.metadata)
        return metadata

    @property
    def embedding_function(self) -> Any:
        """Return the embedding function for this collection."""

        return build_embedding_function(
            provider=self.provider,
            model=self.embedding_model,
        )


@dataclass(slots=True)
class ChromaConfig:
    """Top-level Chroma configuration parsed from JSON."""

    collections: list[CollectionConfig] = field(default_factory=list)

    @classmethod
    def from_path(cls, config_path: Path) -> "ChromaConfig":
        if not config_path.exists():
            raise FileNotFoundError(f"Chroma config not found: {config_path}")

        data = json.loads(config_path.read_text())
        if not isinstance(data, dict):
            raise ValueError("Chroma config must be a JSON object.")

        chroma_data = data.get("chroma")
        if not isinstance(chroma_data, dict):
            raise ValueError("Top-level 'chroma' object is required.")

        collections_data = chroma_data.get("collections", [])
        if not isinstance(collections_data, list):
            raise ValueError("'collections' must be a list inside 'chroma'.")

        collections = [
            CollectionConfig.from_dict(raw, base_dir=config_path.parent)
            for raw in collections_data
        ]
        return cls(collections=collections)


def load_chroma_config(config_path: Path) -> ChromaConfig:
    """Convenience wrapper for loading a Chroma config from JSON."""

    return ChromaConfig.from_path(config_path)


def get_default_collection_and_source(
    config_path: Path,
) -> tuple[str | None, str | None]:
    """
    Return the first collection name and source path from config, or (None, None).

    Does not raise if the file is missing or invalid; callers can decide how to handle.
    """

    try:
        cfg = load_chroma_config(config_path)
    except FileNotFoundError:
        return None, None
    except Exception:
        return None, None

    if not cfg.collections:
        return None, None

    first = cfg.collections[0]
    return first.collection_name, str(first.source_path)
