from __future__ import annotations

import base64
import json
import unittest

from pathlib import Path
from tempfile import TemporaryDirectory

from tools.sync_soc_uxd_knowledge_source import (
    build_markdown_doc_entry,
    build_soc_design_language_collection,
    connect_interaction_principles_spec,
    connect_design_language_spec,
    connect_multilingual_spec,
    DEFAULT_DESIGN_LANGUAGE_REF,
    DEFAULT_HTML,
    DEFAULT_SOURCE,
    ensure_design_language_home_quick_entry,
    ensure_design_language_rules_area_entry,
    ensure_design_language_top_nav_entry,
    ensure_multilingual_home_quick_entry,
    extract_knowledge_docs,
    inject_knowledge_docs,
    sanitize_knowledge_docs,
    upsert_design_language_collection,
    upsert_knowledge_doc,
)


class SocUxdKnowledgeSourceTest(unittest.TestCase):
    def test_extract_knowledge_docs_reads_embedded_json_block(self) -> None:
        html = """
        <script>
        const KNOWLEDGE_DOCS = [{"id":"contracts","title":"Contracts","lines":3}];
        let currentKnowledgeDocId='';
        </script>
        """

        docs = extract_knowledge_docs(html)

        self.assertEqual(docs, [{"id": "contracts", "title": "Contracts", "lines": 3}])

    def test_inject_knowledge_docs_replaces_only_embedded_json_block(self) -> None:
        html = """
        <script>
        const KNOWLEDGE_DOCS = [{"id":"old","title":"Old"}];
        let currentKnowledgeDocId='';
        const UNRELATED = [{"id":"old","title":"Old"}];
        </script>
        """
        docs = [{"id": "new", "title": "New", "lines": 9}]

        updated = inject_knowledge_docs(html, docs)

        self.assertIn('const UNRELATED = [{"id":"old","title":"Old"}];', updated)
        self.assertIn(
            f"const KNOWLEDGE_DOCS = {json.dumps(docs, ensure_ascii=False, indent=2)};",
            updated,
        )

    def test_build_markdown_doc_entry_encodes_source_content(self) -> None:
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "multilingual-spec.md"
            source.write_text("# 多语言与本地化设计规范\n\n正文\n", encoding="utf-8")

            entry = build_markdown_doc_entry(
                doc_id="multilingual-spec",
                title="多语言与本地化设计规范",
                file_label="references/multilingual-spec.md",
                summary="本地化、多语言适配、伪本地化和术语规范。",
                source_path=source,
            )

        self.assertEqual(entry["id"], "multilingual-spec")
        self.assertEqual(entry["lines"], 3)
        self.assertIn("contentB64", entry)

    def test_sanitize_knowledge_docs_rebuilds_bad_summary_from_markdown_body(self) -> None:
        entry = build_markdown_doc_entry(
            doc_id="interaction-document-template",
            title="交互文档模板规范",
            file_label="references/interaction-document-template-spec.md",
            summary="交互文档模板的封面、主画板\ufffd\x19",
            source_path=Path(__file__).resolve().parents[2]
            / ".codex"
            / "skills"
            / "game-interaction-design"
            / "references"
            / "interaction-document-template-spec.md",
        )

        cleaned = sanitize_knowledge_docs([entry])[0]

        self.assertNotIn("\ufffd", cleaned["summary"])
        self.assertNotIn("\x19", cleaned["summary"])
        self.assertIn("交互文档", cleaned["summary"])

    def test_upsert_knowledge_doc_replaces_existing_doc_and_appends_new_doc(self) -> None:
        docs = [{"id": "contracts", "title": "old"}, {"id": "checklists", "title": "check"}]
        replacement = {"id": "contracts", "title": "new"}
        addition = {"id": "multilingual-spec", "title": "多语言"}

        replaced = upsert_knowledge_doc(docs, replacement)
        appended = upsert_knowledge_doc(replaced, addition)

        self.assertEqual(replaced[0], replacement)
        self.assertEqual([doc["id"] for doc in appended], ["contracts", "checklists", "multilingual-spec"])

    def test_connect_multilingual_spec_updates_ready_doc_entries(self) -> None:
        html = """
        {title:'多语言规范',status:'todo',desc:'后续整理文本长度、换行、省略、变量、语言切换与排版约束。'}
        {title:'多语言规范',status:'todo',desc:'待整理文本长度、换行、省略、变量与语言切换约束。'}
        ['多语言规范','后续整理文本长度、换行、省略、变量和语言切换约束。','todo']
        ['多语言规范','rules','todo']
        """

        updated = connect_multilingual_spec(html)

        self.assertNotIn("status:'todo'", updated)
        self.assertIn("doc:'multilingual-spec'", updated)
        updated_again = connect_multilingual_spec(updated)
        self.assertEqual(updated_again, updated)
        self.assertIn("['多语言规范','rules','multilingual-spec','doc']", updated)

    def test_ensure_multilingual_home_quick_entry_adds_final_home_card(self) -> None:
        html = """
        ${[
            ['Prompt system','desc','doc','prompt-system'],
            ['Interface inventory','desc','doc','soc-interface-inventory'],
        ].map(([title,desc,action,id])=>``).join('')}
        """

        updated = ensure_multilingual_home_quick_entry(html)

        self.assertIn("'multilingual-spec'", updated)
        self.assertLess(updated.index("'prompt-system'"), updated.index("'multilingual-spec'"))

    def test_ensure_design_language_entries_add_home_card_and_rules_nav_link(self) -> None:
        home_html = """
        ${[
            ['交互文档模板','desc','doc','interaction-document-template'],
            ['多语言规范','desc','doc','multilingual-spec'],
            ['界面框架规则','desc','doc','fullscreen-framework-translation'],
        ].map(([title,desc,action,id])=>``).join('')}
        """
        nav_html = """
        links:[
            {action:'doc',id:'fullscreen-framework-translation',title:'界面框架与移动转 PC',desc:'desc'},
            {action:'doc',id:'multilingual-spec',title:'多语言规范',desc:'desc'},
        ]
        """

        updated_home = ensure_design_language_home_quick_entry(home_html)
        updated_nav = ensure_design_language_top_nav_entry(nav_html)

        self.assertIn("'doc','soc-design-language'", updated_home)
        self.assertLess(updated_home.index("'multilingual-spec'"), updated_home.index("'soc-design-language'"))
        self.assertIn("id:'soc-design-language',title:'通用设计原则'", updated_nav)
        self.assertLess(updated_nav.index("id:'multilingual-spec'"), updated_nav.index("id:'soc-design-language'"))

    def test_ensure_design_language_rules_area_entry_keeps_collection_after_multilingual(self) -> None:
        html = """
        items:[
          {kind:'doc',doc:'fullscreen-framework-translation',title:'界面框架规则',status:'ready',desc:'desc'},
          {kind:'doc',doc:'multilingual-spec',title:'多语言规范',status:'ready',desc:'desc'},
          {kind:'doc',doc:'soc-design-language',title:'通用设计原则',status:'ready',desc:'复用 Ant Design 17 项设计原则原文结构，作为 SOC UXD 的通用交互设计原则参考。'}
        ]
        """

        updated = ensure_design_language_rules_area_entry(html)

        self.assertEqual(updated.count("doc:'soc-design-language'"), 1)
        self.assertLess(updated.index("doc:'multilingual-spec'"), updated.index("doc:'soc-design-language'"))

    def test_connect_interaction_principles_spec_updates_ready_doc_entries(self) -> None:
        html = """
        {title:'通用交互设计原则',status:'todo',desc:'后续沉淀 SOC 项目的通用交互判断原则。'}
        {title:'通用交互设计原则',status:'todo',desc:'待沉淀 SOC 项目通用交互判断原则。'}
        """

        updated = connect_interaction_principles_spec(html)

        self.assertNotIn("title:'通用交互设计原则',status:'todo'", updated)
        self.assertIn("doc:'soc-interaction-principles'", updated)
        self.assertEqual(connect_interaction_principles_spec(updated), updated)

    def test_default_soc_design_language_source_uses_ant_left_principle_pages(self) -> None:
        collection = build_soc_design_language_collection(DEFAULT_DESIGN_LANGUAGE_REF)

        self.assertEqual(collection["id"], "soc-design-language")
        self.assertEqual(collection["kind"], "collection")
        expected_slugs = [
            "navigation",
            "data-entry",
            "data-display",
            "data-format",
            "copywriting",
            "buttons",
            "data-list",
            "proximity",
            "alignment",
            "contrast",
            "repetition",
            "direct",
            "stay",
            "lightweight",
            "invitation",
            "transition",
            "reaction",
        ]
        self.assertEqual([page["slug"] for page in collection["pages"]], expected_slugs)
        self.assertEqual(collection["groups"], ["通用设计原则"])
        self.assertGreater(collection["lines"], len(expected_slugs) * 20)
        self.assertEqual(
            collection["combinedHtmlFile"],
            "assets/ant-design-spec/combined-cn/ant-spec-combined-clone.html",
        )
        combined_html = base64.b64decode(collection["combinedHtmlB64"]).decode("utf-8")
        self.assertIn('class="layout"', combined_html)
        self.assertIn('class="side"', combined_html)
        self.assertIn('class="toc"', combined_html)
        self.assertIn("page-navigation", combined_html)
        for page in collection["pages"]:
            with self.subTest(page=page["slug"]):
                self.assertTrue(page["slug"])
                self.assertTrue(page["title"])
                self.assertTrue(page["group"])
                self.assertIsInstance(page["order"], int)
                self.assertTrue(page["sourceFile"].endswith(".zh-CN.md"))
                self.assertIn("https://github.com/ant-design/ant-design", page["sourceMdUrl"])
                self.assertIn("https://ant.design/docs/spec/", page["sourcePageUrl"])
                self.assertGreater(page["lines"], 20)
                self.assertIn("contentB64", page)

    def test_upsert_design_language_collection_replaces_old_single_note_entry(self) -> None:
        old_docs = [
            {"id": "contracts", "title": "Contracts"},
            {"id": "soc-interaction-principles", "title": "SOC 通用交互设计原则"},
        ]
        collection = {
            "id": "soc-design-language",
            "kind": "collection",
            "title": "通用设计原则",
            "pages": [],
            "lines": 0,
        }

        updated = upsert_design_language_collection(old_docs, collection)

        self.assertEqual([doc["id"] for doc in updated], ["contracts", "soc-design-language"])

    def test_connect_design_language_spec_replaces_current_principles_entry_with_collection_entry(self) -> None:
        html = """
        {kind:'doc',doc:'soc-interaction-principles',title:'通用交互设计原则',status:'ready',desc:'基于 Ant Design 设计语言内化的 SOC 通用交互原则：上下文、邀请、反馈、状态、文案、导航、动效和组件沉淀。'}
        {action:'doc',id:'soc-interaction-principles',title:'通用交互设计原则',desc:'基于 Ant Design 设计语言内化的 SOC 通用交互原则：上下文、邀请、反馈、状态、文案、导航、动效和组件沉淀。'}
        ['通用交互设计原则','旧说明','doc','soc-interaction-principles']
        """

        updated = connect_design_language_spec(html)

        self.assertNotIn("soc-interaction-principles", updated)
        self.assertIn("doc:'soc-design-language'", updated)
        self.assertIn("id:'soc-design-language'", updated)
        self.assertIn("通用设计原则", updated)
        self.assertEqual(connect_design_language_spec(updated), updated)

    def test_site_html_contains_design_language_collection_rendering_hooks(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn("function renderSOCDesignPrinciples", html)
        self.assertIn("soc-ant-principles-shell", html)
        self.assertIn("soc-ant-page-link", html)
        self.assertIn("soc-ant-toc", html)
        self.assertIn("soc-ant-lightbox", html)
        self.assertIn("function socDecodeBase64Utf8", html)
        self.assertIn("combinedHtmlB64", html)
        self.assertIn("socDesignPrinciplesHtmlCandidates", html)

    def test_site_html_exposes_general_design_principles_entry(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn("title:'通用设计原则'", html)
        self.assertIn("['通用设计原则'", html)
        self.assertNotIn("title:'SOC 设计语言目录'", html)

        rules_link_count = html.count("action:'doc',id:'soc-design-language'")
        self.assertGreaterEqual(rules_link_count, 1)
        self.assertIn("'doc','soc-design-language'", html)

    def test_site_html_strips_markdown_frontmatter_before_rendering(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn("function kbStripFrontmatter", html)
        self.assertIn("kbStripFrontmatter(md)", html)

    def test_site_html_uses_reading_nav_for_single_markdown_docs(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn("function kbReadingNavHtml", html)
        self.assertIn("knowledge-doc-layout", html)
        self.assertIn("const readingNav=kbReadingNavHtml(md);", html)
        self.assertGreaterEqual(html.count("window.scrollTo({top:0,behavior:'auto'});"), 2)

    def test_design_workflow_docs_use_chinese_site_titles(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        titles = {doc["id"]: doc["title"] for doc in docs}

        self.assertEqual(titles["contracts"], "策划输入 / 交互输出契约")
        self.assertEqual(titles["checklists"], "交互检查清单")
        self.assertEqual(titles["skill"], "AI 交互设计流程")

    def test_site_chrome_uses_chinese_labels(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        for visible_english in (
            "KNOWLEDGE DOC",
            "SOC DESIGN KNOWLEDGE BASE",
            "KNOWLEDGE BASE",
            "SOC UXD KNOWLEDGE SYSTEM",
            "Primary paths",
            "Frequent entry",
            "SOC UXD AREA",
            "SOC UXD BUILDING",
            "KNOWLEDGE TEMPLATE",
            "kicker:'Workflow'",
            "kicker:'Rules'",
            "kicker:'Assets'",
            "kicker:'Delivery'",
        ):
            with self.subTest(label=visible_english):
                self.assertNotIn(visible_english, html)

        for chinese_label in (
            "知识文档",
            "SOC UXD 知识系统",
            "常用入口",
            "SOC UXD 分类",
            "SOC UXD 建设中",
            "知识库模板",
            "kicker:'设计流程'",
            "kicker:'规范规则'",
            "kicker:'资产参考'",
            "kicker:'交付落地'",
        ):
            with self.subTest(label=chinese_label):
                self.assertIn(chinese_label, html)

        self.assertNotIn("主要入口", html)

    def test_contract_doc_uses_chinese_boundary_heading(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        contracts = next(doc for doc in docs if doc["id"] == "contracts")
        markdown = base64.b64decode(contracts["contentB64"]).decode("utf-8")

        self.assertIn("## 边界规则", markdown)
        self.assertNotIn("## Boundary Rule", markdown)

    def test_contract_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        contracts = next(doc for doc in docs if doc["id"] == "contracts")

        ai_markdown = base64.b64decode(contracts["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(contracts["webContentB64"]).decode("utf-8")

        self.assertEqual(contracts["webFile"], "web-docs/contracts.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 什么时候使用这篇规范", web_markdown)
        self.assertIn("## 从策划到交互的标准路径", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/contracts-flow.svg", web_markdown)
        self.assertIn("策划输入契约", ai_markdown)
        self.assertIn("交互输出契约", ai_markdown)

    def test_checklists_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        checklists = next(doc for doc in docs if doc["id"] == "checklists")

        ai_markdown = base64.b64decode(checklists["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(checklists["webContentB64"]).decode("utf-8")

        self.assertEqual(checklists["webFile"], "web-docs/checklists.page.md")
        self.assertIn("## 这篇清单解决什么问题", web_markdown)
        self.assertIn("## 什么时候打开这份清单", web_markdown)
        self.assertIn("## 四道检查门", web_markdown)
        self.assertIn("## 检查时怎么判断通过", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/checklists-gates.svg", web_markdown)
        self.assertIn("策划输入检查", ai_markdown)
        self.assertIn("交互输出检查", ai_markdown)
        self.assertGreaterEqual(len(checklists.get("sourceLinks", [])), 4)

    def test_multilingual_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        multilingual = next(doc for doc in docs if doc["id"] == "multilingual-spec")

        ai_markdown = base64.b64decode(multilingual["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(multilingual["webContentB64"]).decode("utf-8")

        self.assertEqual(multilingual["webFile"], "web-docs/multilingual.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 什么时候必须考虑多语言", web_markdown)
        self.assertIn("## 多语言适配的设计路径", web_markdown)
        self.assertIn("## 适配方式怎么选", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/multilingual-flow.svg", web_markdown)
        self.assertIn("文本长度与布局预留", ai_markdown)
        self.assertIn("伪本地化工具规则", ai_markdown)
        self.assertGreaterEqual(len(multilingual.get("sourceLinks", [])), 5)

    def test_ai_interaction_flow_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        skill_doc = next(doc for doc in docs if doc["id"] == "skill")

        ai_markdown = base64.b64decode(skill_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(skill_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(skill_doc["webFile"], "web-docs/ai-interaction-flow.page.md")
        self.assertIn("## 这篇流程解决什么问题", web_markdown)
        self.assertIn("## AI 参与交互设计的工作路径", web_markdown)
        self.assertIn("## 每一步要产出什么", web_markdown)
        self.assertIn("## 什么时候必须回到人工确认", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/ai-interaction-flow.svg", web_markdown)
        self.assertIn("## 读取顺序", ai_markdown)
        self.assertIn("## 核心流程", ai_markdown)
        self.assertGreaterEqual(len(skill_doc.get("sourceLinks", [])), 5)

    def test_interaction_document_template_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        template_doc = next(doc for doc in docs if doc["id"] == "interaction-document-template")

        ai_markdown = base64.b64decode(template_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(template_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(template_doc["webFile"], "web-docs/interaction-document-template.page.md")
        self.assertIn("## 这篇模板解决什么问题", web_markdown)
        self.assertIn("## 什么时候使用这套模板", web_markdown)
        self.assertIn("## 交互文档应该长什么样", web_markdown)
        self.assertIn("## 页面和编号怎么组织", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/interaction-document-template.svg", web_markdown)
        self.assertIn("## 基本原则", ai_markdown)
        self.assertIn("## 标号规则", ai_markdown)
        self.assertGreaterEqual(len(template_doc.get("sourceLinks", [])), 5)

    def test_fullscreen_framework_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        fullscreen_doc = next(doc for doc in docs if doc["id"] == "fullscreen-framework-translation")

        ai_markdown = base64.b64decode(fullscreen_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(fullscreen_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(fullscreen_doc["webFile"], "web-docs/fullscreen-framework-translation.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 什么时候先看框架", web_markdown)
        self.assertIn("## 全屏 View 的标准骨架", web_markdown)
        self.assertIn("## 三类全屏框架怎么判断", web_markdown)
        self.assertIn("## 移动端转 PC 的核心原则", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/fullscreen-framework-translation.svg", web_markdown)
        self.assertIn("## View 标准结构", ai_markdown)
        self.assertIn("## 全屏框架类型判断", ai_markdown)
        self.assertGreaterEqual(len(fullscreen_doc.get("sourceLinks", [])), 5)

    def test_typography_color_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        typography_doc = next(doc for doc in docs if doc["id"] == "typography-color-spec")

        ai_markdown = base64.b64decode(typography_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(typography_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(typography_doc["webFile"], "web-docs/typography-color-spec.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 先按语义选样式", web_markdown)
        self.assertIn("## 字体和字号怎么用", web_markdown)
        self.assertIn("## 字色怎么判断", web_markdown)
        self.assertIn("## 状态色和特殊色怎么用", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/typography-color-spec.svg", web_markdown)
        self.assertIn("## 字体规范", ai_markdown)
        self.assertIn("## 基础字色语义", ai_markdown)
        self.assertGreaterEqual(len(typography_doc.get("sourceLinks", [])), 5)

    def test_figma_node_naming_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        naming_doc = next(doc for doc in docs if doc["id"] == "figma-node-naming-spec")

        ai_markdown = base64.b64decode(naming_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(naming_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(naming_doc["webFile"], "web-docs/figma-node-naming-spec.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 什么时候必须按命名规范", web_markdown)
        self.assertIn("## 标准命名公式", web_markdown)
        self.assertIn("## 顶层 Frame 和全屏结构怎么命名", web_markdown)
        self.assertIn("## 类型前缀怎么选", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/figma-node-naming-spec.svg", web_markdown)
        self.assertIn("## 三、节点命名公式", ai_markdown)
        self.assertIn("## 四、类型前缀表", ai_markdown)
        self.assertGreaterEqual(len(naming_doc.get("sourceLinks", [])), 5)

    def test_interface_layering_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        layering_doc = next(doc for doc in docs if doc["id"] == "interface-layering-spec")

        ai_markdown = base64.b64decode(layering_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(layering_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(layering_doc["webFile"], "web-docs/interface-layering-spec.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 什么时候先判断层级", web_markdown)
        self.assertIn("## SOC 界面层级怎么读", web_markdown)
        self.assertIn("## 设计时怎么选层级", web_markdown)
        self.assertIn("## 字段和双端差异怎么标", web_markdown)
        self.assertIn("## HUD 为什么要单独看", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/interface-layering-spec.svg", web_markdown)
        self.assertIn("## 层级定义", ai_markdown)
        self.assertIn("## UI界面表字段解读", ai_markdown)
        self.assertGreaterEqual(len(layering_doc.get("sourceLinks", [])), 5)

    def test_prompt_system_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        prompt_doc = next(doc for doc in docs if doc["id"] == "prompt-system")

        ai_markdown = base64.b64decode(prompt_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(prompt_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(prompt_doc["webFile"], "web-docs/prompt-system.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 什么时候使用提示系统", web_markdown)
        self.assertIn("## 提示类型怎么选", web_markdown)
        self.assertIn("## 提示强度和队列怎么判断", web_markdown)
        self.assertIn("## 配置来源和字段怎么标", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/prompt-system.svg", web_markdown)
        self.assertIn("## 提示类型总览", ai_markdown)
        self.assertIn("## 队列与优先级", ai_markdown)
        self.assertGreaterEqual(len(prompt_doc.get("sourceLinks", [])), 5)

    def test_figma_patterns_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        figma_doc = next(doc for doc in docs if doc["id"] == "figma-patterns")

        ai_markdown = base64.b64decode(figma_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(figma_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(figma_doc["webFile"], "web-docs/figma-patterns.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 读 Figma 时先看什么", web_markdown)
        self.assertIn("## 写 Figma 时怎么保护源文档", web_markdown)
        self.assertIn("## 组件复用优先级", web_markdown)
        self.assertIn("## 双端转译时怎么落到 Figma", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/figma-patterns.svg", web_markdown)
        self.assertIn("## Figma MCP Workflow", ai_markdown)
        self.assertIn("## Figma Generation Output", ai_markdown)
        self.assertGreaterEqual(len(figma_doc.get("sourceLinks", [])), 5)

    def test_common_components_catalog_doc_has_human_readable_page_source(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        catalog_doc = next(doc for doc in docs if doc["id"] == "soc-common-components-catalog")

        ai_markdown = base64.b64decode(catalog_doc["contentB64"]).decode("utf-8")
        web_markdown = base64.b64decode(catalog_doc["webContentB64"]).decode("utf-8")

        self.assertEqual(catalog_doc["webFile"], "web-docs/soc-common-components-catalog.page.md")
        self.assertIn("## 这篇规范解决什么问题", web_markdown)
        self.assertIn("## 什么时候先查通用组件", web_markdown)
        self.assertIn("## 组件复用怎么判断", web_markdown)
        self.assertIn("## 组件成熟度怎么看", web_markdown)
        self.assertIn("## 常用组件怎么选", web_markdown)
        self.assertIn("## 参考文档索引", web_markdown)
        self.assertIn("assets/soc-uxd/soc-common-components-catalog.svg", web_markdown)
        self.assertIn("## 1. 使用总原则", ai_markdown)
        self.assertIn("## 2. 组件类目总览", ai_markdown)
        self.assertGreaterEqual(len(catalog_doc.get("sourceLinks", [])), 5)

    def test_remaining_reference_docs_have_human_readable_page_sources(self) -> None:
        docs = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        specs = {
            "corpus-notes": {
                "webFile": "web-docs/corpus-notes.page.md",
                "webHeadings": [
                    "## 这篇笔记解决什么问题",
                    "## 这些经验从哪里来",
                    "## 目前沉淀了哪些模式",
                    "## 用它做新设计时怎么查",
                    "## 参考文档索引",
                ],
                "asset": "assets/soc-uxd/corpus-notes.svg",
                "aiSnippets": ["## Source Index", "## Component Library"],
            },
            "ai-figma-fgui": {
                "webFile": "web-docs/ai-figma-fgui.page.md",
                "webHeadings": [
                    "## 这篇流程解决什么问题",
                    "## 从 Figma 到 FGUI 分几步",
                    "## 哪些环节必须人工确认",
                    "## 交付物怎么流转",
                    "## 参考文档索引",
                ],
                "asset": "assets/soc-uxd/ai-figma-fgui.svg",
                "aiSnippets": ["# 流程概要", "# 整体流程控制"],
            },
            "soc-figma-visual-inventory": {
                "webFile": "web-docs/soc-figma-visual-inventory.page.md",
                "webHeadings": [
                    "## 这篇资产库解决什么问题",
                    "## 目前收录了什么",
                    "## 读视觉资产时先看什么",
                    "## 什么时候继续深挖",
                    "## 参考文档索引",
                ],
                "asset": "assets/soc-uxd/soc-figma-visual-inventory.svg",
                "aiSnippets": ["## 总量概览", "## 对后续交互设计的价值"],
            },
            "soc-interface-inventory": {
                "webFile": "web-docs/soc-interface-inventory.page.md",
                "webHeadings": [
                    "## 这篇资产库解决什么问题",
                    "## 界面资产按什么口径整理",
                    "## 查历史界面时看什么",
                    "## 什么时候回到源表",
                    "## 参考文档索引",
                ],
                "asset": "assets/soc-uxd/soc-interface-inventory.svg",
                "aiSnippets": ["# SOC UXD 全量界面资产库", "本页只保留系统级表单结构"],
            },
        }

        for doc_id, spec in specs.items():
            with self.subTest(doc_id=doc_id):
                doc = next(item for item in docs if item["id"] == doc_id)
                ai_markdown = base64.b64decode(doc["contentB64"]).decode("utf-8")
                web_markdown = base64.b64decode(doc["webContentB64"]).decode("utf-8")

                self.assertEqual(doc["webFile"], spec["webFile"])
                for heading in spec["webHeadings"]:
                    self.assertIn(heading, web_markdown)
                self.assertIn(spec["asset"], web_markdown)
                for snippet in spec["aiSnippets"]:
                    self.assertIn(snippet, ai_markdown)
                self.assertGreaterEqual(len(doc.get("sourceLinks", [])), 4)

    def test_site_prefers_human_readable_doc_content_and_renders_reference_index(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn("function kbDocMarkdown", html)
        self.assertIn("doc.webContentB64||doc.contentB64", html)
        self.assertIn("function kbReferenceLinksHtml", html)
        self.assertIn("knowledge-reference-index", html)

    def test_markdown_image_renderer_does_not_lazy_load_doc_figures(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn('decoding="async"><figcaption>${kbEscape(alt)}</figcaption>', html)
        self.assertNotIn('loading="lazy"><figcaption>${kbEscape(alt)}</figcaption>', html)

    def test_site_exposes_byok_question_assistant_without_embedded_secret(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn("soc-assistant-trigger", html)
        self.assertIn("data-soc-assistant-open", html)
        self.assertIn("socAssistantApiKey", html)
        self.assertIn("sessionStorage", html)
        self.assertIn("https://api.openai.com/v1/responses", html)
        self.assertIn("function socAssistantSearch", html)
        self.assertIn("我的 OpenAI API Key", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("SOC_ASSISTANT_API_URL", html)
        self.assertNotIn("Codex API 代理地址", html)

    def test_question_assistant_behaves_like_knowledge_backed_chat(self) -> None:
        html = DEFAULT_HTML.read_text(encoding="utf-8")

        self.assertIn("function socAssistantTestConnection", html)
        self.assertIn("测试连接", html)
        self.assertIn("知识库记忆", html)
        self.assertIn("检索依据", html)
        self.assertIn("回答必须优先综合成自然语言结论", html)
        self.assertIn("请在关键判断后标注对应依据编号", html)
        self.assertIn("你可以把我理解成连接了 SOC UXD 知识库记忆的 ChatGPT", html)


if __name__ == "__main__":
    unittest.main()
