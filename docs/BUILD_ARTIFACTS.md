# Rebuild the course deck and 38-page handbook

This project commits editable source and generated artifacts. The generated PPTX/PDF are **not authoritative**; `.js` and `.md` chapters are the sources. Use them after editing so slide numbers, text and code remain in sync.

## PPTX (Node.js)

```bash
cd slides
npm install
node build_slides.js
```

`slides/package.json` records the `pptxgenjs` dependency. The generated file is `slides/TRACE-QA-Agent-Engineering-Course.pptx` (31 slides in v0.2). Open in PowerPoint or LibreOffice and spot-check page 01, 11, 13, 30, 31 for legibility and version/priority labels. A generated deck is **not** a recording of student mastery or a substitute for the exercises.

## PDF (Python)

```bash
python -m pip install mistune weasyprint
python docs/build_manual_pdf.py
```

Chinese font recommended: Noto Sans CJK SC. Output `docs/TRACE-QA-完整学习与项目说明书.pdf` (38 pages in v0.2 with current layout). WeasyPrint/font versions can change pagination; verify the produced file and page rendering instead of enforcing a fixed page count on other machines.

## Invariants before publishing

- `python -m unittest discover -s tests -v` passes all tests.
- Easy fixture and stress suite are distinct. Do not report one as the other's data.
- Any change to `data/` must regenerate versioned JSON sample outputs (`examples/b0_sample.json`, `examples/b1_sample.json`, `examples/b2_sample.json`) and verify data/corpus hashes before comparison.
- Rebuild PPTX/PDF from current sources; inspect PDF/slide rendering for truncation, unreadable Chinese, tables crossing margins, or broken URLs.
- GitHub remote `main` commit SHA and CI status must be checked after pushing, not assumed.
