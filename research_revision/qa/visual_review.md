Visual review of final local PDFs
=================================

Reviewed on 26 October 2026 using Poppler page renders. Every page was inspected through the rendered contact sheets; the three scientific plots were also inspected separately. No clipped content, overlapping plot labels, missing glyphs, or blank pages was found. The LaTeX log has no overfull or underfull box warnings.

The master is a nine-page author-review document. It is not the later IOCE proceedings template; the first IOCE application is an abstract. The WEAVE PDF is two pages and anonymous. TiP is three pages, including the author block and references, using its requested Times New Roman 12-point body and 1.5 line spacing. IOCE and Urban e-Planning are one page each.

| PDF | Pages inspected | SHA-256 |
|---|---:|---|
| `manuscript/main.pdf` | 9 | `474b18298a10b795033ec26765374040f8d5bcf2babe1536a2d536f82041ac66` |
| `submissions/01-ioce2027/abstract.pdf` | 1 | `9355572c89d6fef2ced597dd27f21c478fe92572a801b99398e7ee008b05ee0e` |
| `submissions/02-weave2027/extended_abstract_blind.pdf` | 2 | `68fd42b9672208610bac453562e51b9a734c89303ce3dc148807848623dea6cf` |
| `submissions/03-tip2027/extended_abstract.pdf` | 3 | `91b5e67f8abc74b294da64e245b135937eec115b0d1afe89b26f4f5d6d3ec612` |
| `submissions/04-urban-eplanning2027/abstract.pdf` | 1 | `7af2b8b3d23299197f7a14282a87781edded2e479e29e9cba25fba42f183b148` |

All body word counts and result strings passed the separate automatic artifact checks. Visual review verifies presentation; scientific checks and source limitations are recorded separately in the analysis outputs and provenance record.

The revised master was re-rendered and all nine pages rechecked after adding the confirmed three-author block and the no-external-funding/no-conflicts declarations. All author names and emails were also verified by text extraction.

The current Yash-first master, IOCE review PDF, anonymous WEAVE PDF, TiP draft and Urban review PDF were rerendered and visually inspected after the confirmed author-order changes. The hashes above refer to these final current artifacts. WEAVE was sent with the exact PDF hash recorded in its receipt.

Urban e-Planning used its official Word form, not the one-page abstract review PDF. The final form was rendered and both pages were inspected under `urban-form-fidelity-02/b_render/`. The form has a 206-word abstract and 99-word biography; the positions row stays together on page 2, and no clipped content, missing glyphs, overlapping text or blank pages was found. The source package and final package differ only in `word/document.xml`: intended right-cell text and the documented position-row pagination repair. All other parts, section geometry, table dimensions, source labels, header/footer relationships and watermark were preserved. Final DOCX SHA-256: `98e2db621f3818d5e480f3173f9ab6e16c41f20d3c6ac11ce44fc2bb5822a2fe`. This exact form was attached to the verified sent email.
