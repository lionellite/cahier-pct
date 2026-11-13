"""Outil de construction du corpus.

Sous-commandes :

    extract   PDF -> texte avec repères de page
    build     PDF ou texte -> extraits JSON + manifeste
    validate  vérifie le corpus actif
    stats     affiche les statistiques du corpus actif

Exemples (depuis backend/) :

    python scripts/corpus.py extract ../corpus/raw/programme-pct-3e.pdf
    python scripts/corpus.py build ../corpus/raw/programme-pct-3e.pdf \
        --config ../corpus/processed/pct-3e/headings.json
    python scripts/corpus.py validate
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

DEFAULT_OUTPUT = ROOT / "corpus" / "processed" / "pct-3e"
PAGE_MARKER = "[[PAGE {number}]]"
PAGE_PATTERN = re.compile(r"^\[\[PAGE (\d+)\]\]\s*$", re.MULTILINE)


@dataclass
class Page:
    number: int
    text: str


def slugify(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", stripped).strip("-").lower()
    return slug or "extrait"


def read_pdf(path: Path) -> list[Page]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[Page] = []
    for index, page in enumerate(reader.pages, start=1):
        pages.append(Page(index, page.extract_text() or ""))
    return pages


def read_text(path: Path) -> list[Page]:
    raw = path.read_text(encoding="utf-8")
    matches = list(PAGE_PATTERN.finditer(raw))
    if not matches:
        return [Page(1, raw)]
    pages: list[Page] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        pages.append(Page(int(match.group(1)), raw[start:end]))
    return pages


def load_pages(path: Path) -> list[Page]:
    if path.suffix.lower() == ".pdf":
        return read_pdf(path)
    if path.suffix.lower() in {".txt", ".md"}:
        return read_text(path)
    raise SystemExit(f"Format non pris en charge : {path.suffix}. Utilisez PDF, TXT ou MD.")


def write_text(pages: list[Page], output: Path) -> None:
    chunks = [f"{PAGE_MARKER.format(number=page.number)}\n{page.text.strip()}\n" for page in pages]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(chunks), encoding="utf-8")


def build_index(pages: list[Page]) -> tuple[str, list[tuple[int, int]]]:
    """Concatène les pages et retourne les offsets de début de page."""
    parts: list[str] = []
    offsets: list[tuple[int, int]] = []
    cursor = 0
    for page in pages:
        offsets.append((cursor, page.number))
        text = page.text.rstrip() + "\n\n"
        parts.append(text)
        cursor += len(text)
    return "".join(parts), offsets


def page_at(offsets: list[tuple[int, int]], position: int) -> int:
    current = offsets[0][1] if offsets else 1
    for start, number in offsets:
        if start <= position:
            current = number
        else:
            break
    return current


def clean(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build(source: Path, config_path: Path, output: Path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    pages = load_pages(source)
    full, offsets = build_index(pages)

    sections = config.get("sections") or []
    if not sections:
        raise SystemExit("Aucune section définie dans la configuration.")

    located: list[tuple[int, dict]] = []
    for section in sections:
        pattern = re.compile(section["start"], re.IGNORECASE)
        match = pattern.search(full)
        if not match:
            print(f"[avertissement] motif introuvable : {section['id']} ({section['start']})")
            continue
        located.append((match.start(), section))

    if not located:
        raise SystemExit("Aucun motif de section trouvé dans le document.")

    located.sort(key=lambda item: item[0])

    manifest_path = output / "manifest.json"
    existing_manifest: dict = {}
    if manifest_path.exists():
        existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    document = config.get("document") or existing_manifest.get("program") or {}
    quarter = output / "extraits"
    quarter.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for index, (start, section) in enumerate(located):
        end = located[index + 1][0] if index + 1 < len(located) else len(full)
        content = clean(full[start:end])
        if not content:
            print(f"[avertissement] section vide ignorée : {section['id']}")
            continue

        first_page = page_at(offsets, start)
        last_page = page_at(offsets, max(start, end - 1))
        pages_range = list(range(first_page, last_page + 1))

        extract_id = section["id"]
        payload = {
            "id": extract_id,
            "level": config.get("level", existing_manifest.get("level", "3e")),
            "type": section.get("type", "section"),
            "title": section.get("title", extract_id),
            "status": "draft",
            "version": 1,
            "source": {
                "document": document.get("title", "Programme officiel"),
                "edition": document.get("edition"),
                "pages": pages_range,
                "url": document.get("url"),
            },
            "metadata": {
                "tags": section.get("tags", []),
                "competences": [],
                "capacites": [],
                "criteres": [],
            },
            "content": content,
        }

        file_name = f"extraits/{index + 1:02d}-{slugify(extract_id)}.json"
        (output / file_name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        entries.append(
            {
                "id": extract_id,
                "title": payload["title"],
                "type": payload["type"],
                "file": file_name,
                "status": "draft",
            }
        )
        print(f"[ok] {extract_id} — {len(content)} caractères, pages {pages_range}")

    manifest = {
        "id": existing_manifest.get("id", output.name),
        "level": config.get("level", existing_manifest.get("level", "3e")),
        "discipline": config.get("discipline", existing_manifest.get("discipline", "PCT")),
        "program": document,
        "expected_extracts": config.get(
            "expected_extracts", existing_manifest.get("expected_extracts", len(entries))
        ),
        "status": "incomplete",
        "updated_at": __import__("datetime").date.today().isoformat(),
        "notes": "Généré par scripts/corpus.py. Chaque extrait doit être relu et passé au statut 'validated' avant publication.",
        "extracts": entries,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\n{len(entries)} extraits écrits dans {output}")
    print(f"Manifeste : {manifest_path}")


def validate(path: Path) -> int:
    from app.services.corpus import Corpus
    from app.errors import CorpusError

    print(f"Validation du corpus : {path}")
    try:
        corpus = Corpus.load(path)
    except CorpusError as exc:
        print(f"[erreur] {exc.message}")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    valid_status = {"demo", "draft", "validated", "deprecated"}

    for extract in corpus.extracts.values():
        if not extract.content.strip():
            errors.append(f"{extract.id} : contenu vide")
        if extract.status not in valid_status:
            errors.append(f"{extract.id} : statut inconnu '{extract.status}'")
        if not extract.source.get("pages"):
            warnings.append(f"{extract.id} : aucune page source")
        if extract.status == "demo":
            warnings.append(f"{extract.id} : extrait de démonstration, à remplacer")

    stats = corpus.stats()
    print(f"- extraits : {stats['extract_count']} / {stats['expected_extracts']}")
    print(f"- validés  : {stats['validated']}")
    print(f"- types    : {', '.join(f'{k}={v}' for k, v in stats['by_type'].items())}")

    for warning in warnings:
        print(f"[avertissement] {warning}")
    for error in errors:
        print(f"[erreur] {error}")

    if errors:
        return 1
    print("Corpus valide.")
    return 0


def stats(path: Path) -> int:
    from app.services.corpus import get_corpus

    corpus = get_corpus(path)
    print(json.dumps(corpus.stats(), ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Outil corpus Cahier PCT")
    sub = parser.add_subparsers(dest="command", required=True)

    extract_parser = sub.add_parser("extract", help="PDF -> texte avec repères de page")
    extract_parser.add_argument("source", type=Path)
    extract_parser.add_argument("--out", type=Path, default=None)

    build_parser = sub.add_parser("build", help="Construire les extraits JSON")
    build_parser.add_argument("source", type=Path)
    build_parser.add_argument("--config", type=Path, required=True)
    build_parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)

    validate_parser = sub.add_parser("validate", help="Valider le corpus")
    validate_parser.add_argument("--path", type=Path, default=DEFAULT_OUTPUT)

    stats_parser = sub.add_parser("stats", help="Statistiques du corpus")
    stats_parser.add_argument("--path", type=Path, default=DEFAULT_OUTPUT)

    args = parser.parse_args(argv)

    if args.command == "extract":
        if not args.source.exists():
            print(f"Fichier introuvable : {args.source}")
            return 1
        pages = load_pages(args.source)
        output = args.out or args.source.with_suffix(".txt")
        write_text(pages, output)
        print(f"{len(pages)} pages extraites -> {output}")
        return 0

    if args.command == "build":
        if not args.source.exists():
            print(f"Fichier introuvable : {args.source}")
            return 1
        if not args.config.exists():
            print(f"Configuration introuvable : {args.config}")
            return 1
        build(args.source, args.config, args.out)
        return 0

    if args.command == "validate":
        return validate(args.path)

    if args.command == "stats":
        return stats(args.path)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
