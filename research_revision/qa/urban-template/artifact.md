# Urban e-Planning 2027 official submission form template contract

Reference: `/Users/yashchauhan/Desktop/minor project/research_revision/submissions/04-urban-eplanning2027/template/official_abstract_form.docx`
SHA-256: `3e225aaae896eed4b5602ade9a9844f092adc1e7ac7ab088e44c99cb9851df1a`
Reference rendering: `page-1.png` and `official_abstract_form.pdf` in this directory; one page inspected. One section. This is an organizer form, not a new document design.

## Page and table system

A4 portrait, 11906 x 16838 twips. Margins: top/bottom 1417 twips, left/right 1701 twips. Header/footer distances 708 twips. One column. Page numbering starts at 1 but no page-number field exists. Source first/even/default header/footer relationships remain unchanged. No added section breaks.

One fixed-layout two-column table: width 10065 twips, indent -318 twips, grid 3261 and 6804 twips. Preserve source cell widths, margins, vertical alignment, row minimum heights, splitting behavior, black single borders (size 4), and gray divider row. Filled cells expand naturally; an additional page is expected for 206 abstract words plus author details and biography. Never shrink fonts to force the empty form's single page.

## Typography and components

Source headings, conference/organizer/date paragraphs, and the gray diagonal Urban e-Planning Conference 2027 watermark remain unchanged. All paragraphs use source Normal style and direct formatting. Default text is 11 point; source right-cell title/author/presenter/position/postal/bio runs use Candara 12 point, title bold. Abstract, keywords, affiliation, and email slots inherit source Candara 11 point from their paragraph run properties and document defaults. Reuse the corresponding source run and paragraph properties exactly, including alignment, spacing, line spacing, keep rules, tabs, indents, and black/theme color behavior. Exact XML evidence for every paragraph role is in `template_structure.json`; no generic styles are applied. Template style-lint results are in `style-evidence.json`.

The header/date block precedes the form. The two-column label/value design and watermark are the only recurring visual components. There are no lists, content controls, bookmarks, comments, cross-reference/page fields, illustrations, or nonempty footnotes/endnotes to fill. Header/footer parts are blank and preserved; the watermark is a VML pict in the document part, preserved byte structurally outside cells.

## Editable slot map

Stable locator: `word/document.xml`, sole `w:tbl`, zero-based row index, right `w:tc[2]`. These value cells may change. A documented pagination repair may add cantSplit to row 7 (Position) so its three author positions and label stay together; otherwise left labels, row properties, table geometry and surrounding paragraphs are preserve-only.

- Row 0: paper title, source title run properties; one paragraph.
- Row 1: 200–250 word abstract, source paragraph pattern; three cloned paragraphs permitted.
- Row 2: 4–5 keyword terms; one paragraph.
- Row 3: gray blank divider, preserve-only.
- Row 4: three authors in confirmed Yash, Suresh, Shreya order; one paragraph.
- Row 5: Yash, corresponding author and proposed online presenter; one paragraph. No unverified full-attendance promise.
- Row 6: common confirmed department/university affiliation; one paragraph.
- Row 7: actual current academic positions, confirmed by user; three cloned source paragraphs.
- Row 8: institutional postal address verified from SRM RTI PDF; one paragraph.
- Row 9: all three institutional email addresses; three cloned source paragraphs. Yash's active address confirmed by user.
- Row 10: approximately 100 words, group biographical note limited to confirmed roles/affiliation and this study; one paragraph.

Within an editable cell, retain its original first paragraph properties; clone those properties for additional paragraphs. Reuse its source first-run properties or paragraph run properties. Plain text only; there are no relationship-backed editable slots. No unsupported optional slots need removal. All required slots are now supported by confirmed facts.

## Package preservation and fidelity gates

Full package-part paths, byte sizes and hashes are in `package_inventory.json`. Only `word/document.xml` may change, and only the right-cell content and the row 7 keep-together pagination repair enumerated above. Every other package part (including core properties, styles, theme, settings, relationships, opaque parts, VML watermark dependencies, header/footer parts, and footnote/endnote parts) must remain byte-for-byte equal. Preserve original zip entry metadata. Undoing the right-cell edits and row 7 cantSplit addition in an XML copy must exactly reproduce the parsed original document part.

Verify reference hash before/after authoring, equal package inventories and all preserve-only hashes, identical section/table properties, and unchanged surrounding XML. Render final and compare with the retained reference via render_and_diff.py. Inspect every final page at full resolution for clipped or missing text, awkward row splits, border/watermark/header movement, blanks, and font substitution defects. Additional pages caused by filled slots are expected; no unrelated layout changes are allowed. Run source/final section and style audits. No field refresh is needed (zero fields).

## Visual iteration 1

The first filled render split the short Position label and author list across pages. The final scope includes a cantSplit property on row 7, preserving fonts, dimensions, labels and content while moving the complete position row to page 2. This is the only source row-flow adjustment.
