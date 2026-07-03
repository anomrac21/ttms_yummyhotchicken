#!/usr/bin/env python3
"""Update content/*/_index.md to icon + images.primary (client-owned assets)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGES_DIR = ROOT / "static" / "images"

SECTIONS: dict[str, str] = {
    "promotions": "chicken-header.webp",
    "new-orleans-roasted-wings": "chicken-combo-header.png",
    "signature-combos": "combos.webp",
    "yummy-fried-chicken": "chicken-header.webp",
    "crispy-combos": "crispy-chicken-tenders-combo.webp",
    "premium-burger-combos": "classic-beef-burger-combo.webp",
    "yummy-burgers": "burger-header.webp",
    "family-feasts": "fam-header.webp",
    "signature-fruit-mix": "signature-fruit-mix.webp",
    "smashed-lemon-tea": "signature-fruit-mix.webp",
    "light-milk-fresh-tea": "signature-fruit-mix.webp",
    "premium-toppings-milk-tea": "signature-fruit-mix.webp",
    "juicy-fruit-ice-blends": "juicy-fruit-ice-blends.webp",
    "island-fresh-milk-smoothies": "juicy-fruit-ice-blends.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def legacy_section_image(raw: str) -> str | None:
    for key in ("image", "top"):
        m = re.search(rf"^\s*{key}:\s*(.+)$", raw, re.M)
        if not m:
            continue
        path = m.group(1).strip()
        if path.startswith("images/"):
            return path.split("/", 1)[1]
        if not path.startswith("http") and not path.startswith("/"):
            return path
    return None


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    legacy = legacy_section_image(raw)
    if legacy and (IMAGES_DIR / legacy).exists():
        image_file = legacy

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>Crispy fried chicken, New Orleans–style wings, burgers, and "
            "<strong>Yummy Tea</strong> — all in one menu.</p>"
        )
    text = (
        "---\n"
        'title: "Yummy Hot Chicken"\n'
        f"image: {img('chicken-header.webp')}\n"
        "images:\n"
        f"    - image: {img('chicken-header.webp')}\n"
        f"    - image: {img('burger-header.webp')}\n"
        f"    - image: {img('combos.webp')}\n"
        f"    - image: {img('signature-fruit-mix.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('chicken-header.webp')}\n"
        f"    - image: {img('chicken-combo-header.png')}\n"
        f"    - image: {img('burger-header.webp')}\n"
        f"    - image: {img('fam-header.webp')}\n"
        f"    - image: {img('party-bucket-royale.webp')}\n"
        f"    - image: {img('juicy-fruit-ice-blends.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    slideshow = [
        "chicken-header.webp",
        "chicken-combo-header.png",
        "burger-header.webp",
        "fam-header.webp",
        "party-bucket-royale.webp",
        "juicy-fruit-ice-blends.webp",
    ]
    missing: list[str] = []
    for section, image_file in SECTIONS.items():
        if not (IMAGES_DIR / image_file).exists():
            missing.append(f"{section} → {image_file}")
    for name in slideshow:
        if not (IMAGES_DIR / name).exists():
            missing.append(f"slideshow → {name}")

    if missing:
        print("Missing images:")
        for line in missing:
            print(f"  {line}")
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    update_home_index()

    credits = "\n".join(
        f"- {name} — Yummy Hot Chicken (client-owned)"
        for name in sorted(set(SECTIONS.values()))
    )
    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos (client-owned menu photography):\n" + credits + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
