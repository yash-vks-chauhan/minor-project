"""Fill the organizer's retained DOCX through a scoped OOXML package patch."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "submissions/04-urban-eplanning2027"
REFERENCE = TARGET / "template/official_abstract_form.docx"
OUTPUT = TARGET / "Urban_ePlanning_2027_Yash_Chauhan.docx"
QA = ROOT / "qa/urban-template"
EXPECTED_REFERENCE_HASH = "3e225aaae896eed4b5602ade9a9844f092adc1e7ac7ab088e44c99cb9851df1a"
HELPER = Path("/Users/yashchauhan/.codex/plugins/cache/openai-primary-runtime/documents/26.1025.11240/skills/documents/scripts/docx_ooxml_patch.py")
spec = importlib.util.spec_from_file_location("docx_ooxml_patch", HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
qn = helper._qn
NS = helper.NS

BIO = (
    "Yash Chauhan and Shreya Srivastava are undergraduate students, and Suresh Kumar "
    "Chelliah is an assistant professor in the Department of Computational Intelligence "
    "at SRM Institute of Science & Technology, Kattankulathur, India. For this study, "
    "Yash led conceptualization, methodology, software, data curation, formal analysis, "
    "validation, visualization, and manuscript drafting and revision. Suresh provided "
    "supervision. Shreya contributed to investigation and manuscript review and editing. "
    "Yash is the corresponding author and proposed online presenter. Their collaborative "
    "work examines digital access, sustainability indicators, and formal e-waste "
    "processing across Indian states, with attention to public-data provenance, "
    "statistical uncertainty, and the limits of regional measurement."
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fill_cell(cell, paragraphs: list[str]):
    """Reuse a source paragraph/run pattern; edit only the designated right cell."""
    source_p = cell.find("w:p", NS)
    assert source_p is not None
    source_ppr = source_p.find("w:pPr", NS)
    source_run = source_p.find("w:r", NS)
    source_rpr = source_run.find("w:rPr", NS) if source_run is not None else None
    if source_rpr is None and source_ppr is not None:
        source_rpr = source_ppr.find("w:rPr", NS)
    for index, text in enumerate(paragraphs):
        if index == 0:
            paragraph = source_p
            for child in list(paragraph):
                if child.tag != qn("w", "pPr"):
                    paragraph.remove(child)
        else:
            paragraph = etree.Element(qn("w", "p"))
            if source_ppr is not None:
                paragraph.append(copy.deepcopy(source_ppr))
            cell.append(paragraph)
        run = etree.SubElement(paragraph, qn("w", "r"))
        if source_rpr is not None:
            run.append(copy.deepcopy(source_rpr))
        text_node = etree.SubElement(run, qn("w", "t"))
        text_node.text = text


def main():
    assert digest(REFERENCE.read_bytes()) == EXPECTED_REFERENCE_HASH
    assert (QA / "artifact.md").exists(), "Template contract required before authoring"
    abstract = (TARGET / "abstract_body.txt").read_text().strip()
    assert 200 <= len(abstract.split()) <= 250
    assert 90 <= len(BIO.split()) <= 110
    slots = {
        0: ["Digital Access and Circularity-Related Regional Indicators in Indian States"],
        1: abstract.split("\n\n"),
        2: ["Digital access; regional planning; circular economy; sustainability indicators; e-waste"],
        4: ["Yash Chauhan; Suresh Kumar Chelliah; Shreya Srivastava"],
        5: ["Yash Chauhan — online presenter and corresponding author"],
        6: ["Department of Computational Intelligence, SRM Institute of Science & Technology, Kattankulathur, Tamil Nadu, India"],
        7: ["Yash Chauhan — Undergraduate student", "Suresh Kumar Chelliah — Assistant professor", "Shreya Srivastava — Undergraduate student"],
        8: ["SRM Institute of Science & Technology, SRM Nagar, Kattankulathur 603203, Chengalpattu District, Tamil Nadu, India"],
        9: ["Yash Chauhan: yc0810@srmist.edu.in", "Suresh Kumar Chelliah: sureshkc@srmist.edu.in", "Shreya Srivastava: ss1371@srmist.edu.in"],
        10: [BIO],
    }
    with ZipFile(REFERENCE) as original:
        xml = etree.fromstring(original.read("word/document.xml"))
        baseline = copy.deepcopy(xml)
        assert not xml.xpath("//w:sdt|//w:instrText|//w:fldSimple", namespaces=NS)
        rows = xml.xpath("//w:tbl/w:tr", namespaces=NS)
        for row_index, content in slots.items():
            fill_cell(rows[row_index].findall("w:tc", NS)[1], content)
        # Keep the three short position lines and their label together on page 2.
        # This is the sole pagination repair to the source's default row behavior.
        position_properties = rows[7].find("w:trPr", NS)
        etree.SubElement(position_properties, qn("w", "cantSplit"))
        # All content outside the intended right-hand slots must remain identical.
        scrubbed = copy.deepcopy(xml)
        scrubbed_rows = scrubbed.xpath("//w:tbl/w:tr", namespaces=NS)
        baseline_rows = baseline.xpath("//w:tbl/w:tr", namespaces=NS)
        for index in slots:
            altered = scrubbed_rows[index].findall("w:tc", NS)[1]
            altered.getparent().replace(altered, copy.deepcopy(baseline_rows[index].findall("w:tc", NS)[1]))
        scrubbed_rows[7].find("w:trPr", NS).remove(scrubbed_rows[7].find("w:trPr/w:cantSplit", NS))
        assert etree.tostring(scrubbed) == etree.tostring(baseline)
        with ZipFile(OUTPUT, "w") as final:
            for info in original.infolist():
                data = etree.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True) if info.filename == "word/document.xml" else original.read(info.filename)
                final.writestr(copy.copy(info), data)
        with ZipFile(OUTPUT) as final:
            assert final.namelist() == original.namelist()
            changed = [name for name in original.namelist() if original.read(name) != final.read(name)]
            assert changed == ["word/document.xml"], changed
    assert digest(REFERENCE.read_bytes()) == EXPECTED_REFERENCE_HASH
    record = {"reference_sha256": EXPECTED_REFERENCE_HASH, "output_sha256": digest(OUTPUT.read_bytes()), "changed_package_parts": changed, "preserved_package_parts": True, "preserved_outside_editable_cells_and_documented_pagination_repair": True, "pagination_repair": "Position row 7 cantSplit prevents its label and authors being divided across pages", "abstract_words": len(abstract.split()), "bio_words": len(BIO.split()), "positions_source": "User confirmed Yash and Shreya undergraduate students and Suresh assistant professor on 26 October 2026", "institutional_email_confirmed_active": "yc0810@srmist.edu.in", "output": str(OUTPUT)}
    (TARGET / "form_fields.json").write_text(json.dumps(slots, indent=2, ensure_ascii=False) + "\n")
    (QA / "package_verification.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
