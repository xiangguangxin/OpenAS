# XLSX 编写示例 / Authoring example

在任务目录使用已配置的 Python 环境；本例使用 openpyxl，生成实际公式并重开验证，但不宣称已有计算缓存。标识符按文本保存，数字格式只控制显示。

Use the configured interpreter in the task directory. This openpyxl example writes real formulas and reopens them without claiming refreshed caches. Identifiers remain text; number formats affect display only.

```python
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

output = Path('report.xlsx')
if output.exists():
    raise FileExistsError(output)
workbook = Workbook()
sheet = workbook.active
sheet.title = 'Revenue'
for row in [('ID', 'Amount'), ('001', 12), ('002', 18), ('Total', '=SUM(B2:B3)')]:
    sheet.append(row)
for cell in sheet[1]:
    cell.font = Font(bold=True)
for row in sheet.iter_rows(min_row=2, max_row=4, min_col=2, max_col=2):
    row[0].number_format = '0.00'
workbook.save(output)
workbook.close()
check = load_workbook(output, data_only=False)
assert check['Revenue']['A2'].value == '001'
assert check['Revenue']['B4'].value == '=SUM(B2:B3)'
check.close()
```

要核对“B4 已计算为 30”，需使用 office-recalculate 所述真实引擎刷新后，分别重开检查公式与缓存；不要将公式改为 30。pandas 结果应按目标范围写回，不能用 DataFrame 覆盖整个原工作簿。

To verify a cached B4 result of 30, refresh through the real engine described by office-recalculate and reopen formulas/caches separately. Do not replace the formula with 30. Write pandas results into intended ranges rather than overwriting an existing workbook with a DataFrame.
