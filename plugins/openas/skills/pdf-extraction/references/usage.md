# 提取接口与验证 / Extraction interface and validation

## 中文

使用项目选定的 Python，已有 Office 环境可直接复用。脚本仅依赖 pypdf，版本来自 office/requirements.txt；不需要系统 Office 引擎。加密算法可能额外需要 pypdf 的可选密码学依赖，缺失时报告环境限制，不自动安装。

```bash
python3 /path/to/OpenAS/plugins/openas/skills/pdf-extraction/scripts/extract_pdf.py /task/input.pdf --output-dir /task/new-text
python3 /path/to/OpenAS/plugins/openas/skills/pdf-extraction/scripts/extract_pdf.py /task/input.pdf --output-dir /task/new-selected --pages 1,3-5 --format json
python3 /path/to/OpenAS/plugins/openas/skills/pdf-extraction/scripts/extract_pdf.py /task/input.pdf --output-dir /task/new-layout --mode layout --format txt
```

- --pages 省略为全部实际 PDF 页；允许单页、逗号和闭区间。按请求顺序输出，重复、重叠、倒序区间及越界均拒绝。页 3,1 表示先第 3 页再第 1 页；区间 3-1 无效。
- --format 为 txt / json / both，默认 both；--mode 为 plain / layout，默认 plain。输出目录必须不存在，不覆盖原稿或旧结果。
- 用户提供密码时可用 --password-file /task/password.txt，读取该文件的密码并仅去掉末尾换行；参数本身不含密码。不提交密码文件或将其列入报告，不尝试字典破解。
- text.txt 使用带页号/状态的分隔标题，错误/空文本页使用明确标记，不能把这些标记当原始 PDF 内容。pages.json 保留原文字字符串；错误页 text 为 null，空文本页为 "" 或实际空白字符串。
- extraction-report.json 包含源/输出 SHA-256、总页数、选页、逐页状态/字符数、empty_pages、failed_pages 及 ocr_performed=false，不回显全文或密码。

退出 0：选页均完成解析；status 可能是 completed 或 needs_review，后者表示至少一页没有提取出文字。退出 1：页级解析失败，status 为 partial 或 failed，保留结果。退出 2：输入、密码、依赖、输出等错误；预检查失败不创建输出目录。中断/写盘错误不报告完成，可写时保留 failed 报告。

样例检查应覆盖有文字的选页、真实空白页、只有图像的页面、重叠/越界选择、加密与错误密码、页级解析异常和原文件保护。对 image-only 页应观察到 no_text / OCR 提示，不伪造识别文字；空白页也可能得到相同提示，需另行判断。表格和扫描识别不在本脚本能力范围内。

提取可能占用较多内存，选页并不保证解析器只读取选中页的数据。大文档在有资源限制的执行环境运行，并按任务设执行时限；脚本不承诺对任意复杂 PDF 的固定资源上限。来源文字可能含敏感内容，产物按任务既有目录和分享范围处理。

## English

Use the project interpreter, reusing an existing Office environment where available. Only pypdf is needed; its pin is in office/requirements.txt. No Office engine is required. Some encryption algorithms need optional cryptographic dependencies; report absence without automatic installation.

The commands above support all pages or comma-separated 1-based physical pages/inclusive ranges, preserving requested order. Reject overlaps, duplicates, reversed ranges, and out-of-range pages. Format is txt/json/both (default both); mode is plain/layout (default plain). Output directories must be new.

A supplied --password-file reads the password while removing trailing newlines only, without placing it in argv/reports or attempting cracking. Keep password files outside committed/delivered outputs. text.txt has explicit page/status markers; they are not PDF source text. pages.json preserves text strings, null for errors, and empty/whitespace strings for no_text. The report contains hashes, page provenance, statuses/counts, empty/error lists and ocr_performed=false, without full text or passwords.

Exit 0 means selected pages were processed: completed or needs_review for empty text. Exit 1 means page-level errors with partial/failed results retained. Exit 2 covers input/password/dependency/output errors; preflight failures create no output directory. Interruptions/write failures do not claim completion; failed reports are retained when writable.

Check actual text, blank/image-only pages, selections, encryption/password failures, parser exceptions, and source preservation. Image-only pages need inspection/OCR rather than invented text; genuine blanks can produce the same hint. Table reconstruction and OCR are unsupported. Selection does not guarantee page-local parser memory use: run large/complex PDFs under host resource/time limits instead of assuming fixed bounds. Preserve existing handling/sharing scope for potentially sensitive source text.
