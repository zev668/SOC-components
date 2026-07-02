from __future__ import annotations

import json
import unittest
import zipfile

from pathlib import Path
from tempfile import TemporaryDirectory

from tools.ingest_soc_uxd_documents import SourceSpec, build_document_library, read_xlsx_catalog
from tools.sync_soc_uxd_knowledge_source import DEFAULT_HTML
from tools.build_soc_uxd_inventory import build_inventory_markdown


class SocUxdDocumentLibraryTest(unittest.TestCase):
    def write_minimal_xlsx(self, path: Path, *, dimension: str = "A1:C3") -> None:
        workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="术语表" sheetId="1" r:id="rId1"/></sheets></workbook>"""
        workbook_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>"""
        sheet = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="{dimension}"/><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c></row><row r="2"><c r="A2" t="s"><v>3</v></c><c r="B2" t="s"><v>4</v></c><c r="C2" t="s"><v>5</v></c></row><row r="3"><c r="A3" t="s"><v>6</v></c><c r="B3" t="s"><v>7</v></c><c r="C3" t="s"><v>8</v></c></row></sheetData></worksheet>"""
        shared = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="9" uniqueCount="9"><si><t>中文</t></si><si><t>英文</t></si><si><t>备注</t></si><si><t>开始游戏</t></si><si><t>Start</t></si><si><t>按钮</t></si><si><t>背包</t></si><si><t>Inventory</t></si><si><t>系统名</t></si></sst>"""
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("xl/workbook.xml", workbook)
            archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            archive.writestr("xl/worksheets/sheet1.xml", sheet)
            archive.writestr("xl/sharedStrings.xml", shared)

    def test_read_xlsx_catalog_extracts_sheet_names_headers_and_samples(self) -> None:
        with TemporaryDirectory() as tmp:
            workbook_path = Path(tmp) / "terms.xlsx"
            self.write_minimal_xlsx(workbook_path)

            markdown = read_xlsx_catalog(workbook_path, sample_rows=2)

        self.assertIn("# terms", markdown)
        self.assertIn("## Sheet: 术语表", markdown)
        self.assertIn("- 维度：A1:C3", markdown)
        self.assertIn("- 表头：中文 | 英文 | 备注", markdown)
        self.assertIn("| 开始游戏 | Start | 按钮 |", markdown)
        self.assertIn("| 背包 | Inventory | 系统名 |", markdown)

    def test_read_xlsx_catalog_infers_sampled_dimension_when_workbook_reports_a1(self) -> None:
        with TemporaryDirectory() as tmp:
            workbook_path = Path(tmp) / "terms.xlsx"
            self.write_minimal_xlsx(workbook_path, dimension="A1")

            markdown = read_xlsx_catalog(workbook_path, sample_rows=2)

        self.assertIn("- 维度：A1:C3（采样推断）", markdown)

    def test_build_document_library_writes_manifest_documents_and_chunks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "本地化设计共识与落地规范.md"
            source.write_text(
                "# 本地化设计共识与落地规范\n\n"
                "## 文本长度\n\n"
                "所有按钮文案需要预留文本膨胀空间。\n\n"
                "## 待确认\n\n"
                "术语表中的台英翻译需要负责人确认。\n",
                encoding="utf-8",
            )
            out = root / "data" / "soc-uxd"

            manifest = build_document_library(
                [
                    SourceSpec(
                        doc_id="localization-consensus",
                        title="本地化设计共识与落地规范",
                        path=source,
                        topics=["多语言规范"],
                    )
                ],
                output_root=out,
                source_root=root,
                generated_at="2026-07-02T00:00:00+08:00",
            )

            self.assertEqual(manifest["version"], 1)
            self.assertEqual(len(manifest["documents"]), 1)
            entry = manifest["documents"][0]
            self.assertEqual(entry["docId"], "localization-consensus")
            self.assertEqual(entry["sourceType"], "md")
            self.assertEqual(entry["publishStatus"], "converted")
            self.assertEqual(entry["documentPath"], "documents/localization-consensus.md")
            self.assertEqual(entry["chunkPath"], "chunks/localization-consensus.jsonl")
            self.assertGreaterEqual(entry["chunkCount"], 1)

            document = out / entry["documentPath"]
            chunks = out / entry["chunkPath"]
            self.assertTrue(document.exists())
            self.assertTrue(chunks.exists())
            document_text = document.read_text(encoding="utf-8")
            self.assertIn("## 文档身份", document_text)
            self.assertIn("## 原文结构转写", document_text)
            self.assertIn("## 明确规则 / 决策", document_text)
            chunk_rows = [
                json.loads(line)
                for line in chunks.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(chunk_rows[0]["docId"], "localization-consensus")
            self.assertIn("source", chunk_rows[0])
            self.assertIn("多语言规范", chunk_rows[0]["tags"])

    def test_site_exposes_document_center_and_loads_library_chunks(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn("function renderSOCDocumentCenter", html)
        self.assertIn("data/soc-uxd/manifest.json", html)
        self.assertIn("function socAssistantEnsureDocumentLibraryLoaded", html)
        self.assertIn("SOC_DOCUMENT_LIBRARY_CHUNKS", html)
        self.assertIn("资料库", html)
        self.assertIn("资料库 / 下载中心", html)

    def test_current_excel_sources_are_cataloged_for_retrieval(self) -> None:
        manifest = json.loads((DEFAULT_HTML.parent / "data" / "soc-uxd" / "manifest.json").read_text(encoding="utf-8"))
        xlsx_docs = [doc for doc in manifest["documents"] if doc["sourceType"] == "xlsx"]

        self.assertEqual(len(xlsx_docs), 4)
        for doc in xlsx_docs:
            with self.subTest(doc=doc["docId"]):
                self.assertEqual(doc["publishStatus"], "converted")
                self.assertGreater(doc["chunkCount"], 12)
                markdown = (DEFAULT_HTML.parent / "data" / "soc-uxd" / doc["documentPath"]).read_text(encoding="utf-8")
                self.assertIn("这是 Excel 目录级解析", markdown)
                self.assertIn("## Sheet:", markdown)
                self.assertIn("表头：", markdown)

    def test_inventory_markdown_lists_human_docs_source_docs_and_gaps(self) -> None:
        markdown = build_inventory_markdown()

        self.assertIn("# SOC UXD 知识库当前盘点", markdown)
        self.assertIn("## 已沉淀的可读网页文档", markdown)
        self.assertIn("## 已入库的原始资料 / AI 检索文档", markdown)
        self.assertIn("## 当前缺口和下一步补充方向", markdown)
        self.assertIn("策划输入 / 交互输出契约", markdown)
        self.assertIn("本地化设计共识与落地规范", markdown)
        self.assertIn("data/soc-uxd/chunks/*.jsonl", markdown)

    def test_current_manifest_registers_inventory_as_first_retrieval_source(self) -> None:
        manifest = json.loads((DEFAULT_HTML.parent / "data" / "soc-uxd" / "manifest.json").read_text(encoding="utf-8"))
        first = manifest["documents"][0]

        self.assertEqual(first["docId"], "soc-uxd-current-inventory")
        self.assertEqual(first["documentPath"], "SOC-UXD-知识库当前盘点.md")
        self.assertGreater(first["chunkCount"], 1)


if __name__ == "__main__":
    unittest.main()
