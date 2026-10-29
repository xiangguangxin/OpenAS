# DOCX 编写示例 / Authoring example

在任务目录使用已配置的 Python 环境运行。新文件应不存在；下面生成一个含独立 runs 的小文档，再通过另一段代码定点修改并保留邻近样式。实际任务按其真实段落与 runs 定位，不把本例文本当通用匹配规则。

Run in the task directory with the configured interpreter. New output files must not exist. These examples create independent runs and perform a targeted edit preserving adjacent styling; locate real paragraphs/runs for actual tasks.

```python
from pathlib import Path
from docx import Document

output = Path('report.docx')
if output.exists():
    raise FileExistsError(output)
document = Document()
document.add_heading('Project report', 0)
paragraph = document.add_paragraph()
paragraph.add_run('Draft').bold = True
paragraph.add_run(' technical summary').italic = True
document.add_table(rows=1, cols=2).rows[0].cells[0].text = 'Scope'
document.save(output)
check = Document(output)
assert check.paragraphs[1].text == 'Draft technical summary'
```

```python
from pathlib import Path
from docx import Document

output = Path('edited.docx')
if output.exists():
    raise FileExistsError(output)
document = Document('report.docx')
paragraph = next(p for p in document.paragraphs if p.text == 'Draft technical summary')
run = next(r for r in paragraph.runs if r.text == 'Draft')
run.text = 'Final'
document.save(output)
check = Document(output)
assert check.paragraphs[1].text == 'Final technical summary'
assert check.paragraphs[1].runs[0].bold
assert check.paragraphs[1].runs[1].italic
```

这些检查只覆盖文字和示例格式，不生成分页预览或证明 Word 原生保真；复杂修订与 OOXML 特性不由本例处理。

Checks cover text and the demonstrated formatting only, without pagination previews, native Word fidelity, or complex revision/OOXML support.
