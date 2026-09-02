from pathlib import Path

import pytest

from app.ingestion.loader import extract_text_from_pdf


def test_loader_raises_for_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(str(tmp_path / "missing.pdf"))
