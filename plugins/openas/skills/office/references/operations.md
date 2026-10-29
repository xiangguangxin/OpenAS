# Office 操作与环境 / Operations and environments

## 中文

优先使用项目指定的解释器和已经配置的工具。`office/requirements.txt` 固定了 DOCX、XLSX 和 PDF 解析用的可选 Python 库；不是所有操作都需要整套依赖。仅在当前授权范围内安装到隔离环境，不写入技能目录或改变系统 Python。脚本不下载工具、不调用外部转换服务。

| 操作 | Python / 本地工具 | 实际检查 |
| --- | --- | --- |
| DOCX 创建/定点编辑 | python-docx | 重开检查内容和相关格式，不分页 |
| XLSX 创建/定点编辑 | openpyxl | 重开检查类型、公式和工作簿，不执行公式 |
| export-pdf | 标准库 + LibreOffice | 退出码、预期非空文件、PDF 签名 |
| render（已有 PDF） | pypdf + pdftoppm | 解析页数、指定页范围、PNG 签名 |
| render（Office 文件） | 上述渲染依赖 + LibreOffice | 导出后按 PDF 页渲染 |
| recalculate | openpyxl + LibreOffice | 公式映射不变、缓存存在、无公式错误；业务值另查 |

将下列 `/path/to/OpenAS` 和任务路径替换为真实位置，使用选定环境的 Python：

```bash
python3 /path/to/OpenAS/plugins/openas/skills/office/scripts/office_ops.py export-pdf /task/report.docx --output-dir /task/new-pdf
python3 /path/to/OpenAS/plugins/openas/skills/office/scripts/office_ops.py render /task/report.pdf --output-dir /task/new-images --pages 1,3
python3 /path/to/OpenAS/plugins/openas/skills/office/scripts/office_ops.py recalculate /task/report.xlsx --output-dir /task/new-calculation
```

输入限 DOCX/XLSX/PPTX；render 另接受 PDF，recalculate 仅接受本地普通 XLSX。`--pages` 是逗号分隔的一基 PDF 页号，仅用于 render；省略时渲染全部页面。XLSX 按已有打印布局转换，无 sheet/range 选项，不能把 PDF 页号当工作表号。

`--soffice /installed/path/soffice`、`--pdftoppm /installed/path/pdftoppm` 可指定不在 PATH 中的既有工具。`--timeout` 是整个外部命令链的时间预算，默认 120 秒，超时/中断会终止并等待本次进程组。不会关闭用户已有 Office 进程。

输出目录必须不存在，原稿、旧结果和用户 Office profile 均保留。导出产物是 document.pdf，重算是 recalculated.xlsx，图片为 pages/page-NNNN.png；operation-report.json 记录源/输出指纹、操作状态和实际检查，operation.log 保留工具诊断。预检查失败不会创建输出目录；执行失败保留已生成的结果和 failed 报告。visual_review 始终为 not_run，需由实际查看图片的执行者另行报告。

PDF 导出不自动生成图片或执行重算。PNG 签名检查不证明图像可读或布局正确。重算在临时副本中清空旧缓存并请求自动完整计算，避免旧缓存原样透传；openpyxl 暂存往返不承诺高级特性保真。重算拒绝已识别的外部连接、链接、宏及外部数据公式，也不验收数组/数据表公式；不是外部数据刷新或任意 Excel 兼容方案。业务正确性、样式/高级特性保留和原生 Office 验收仍由任务相关检查承担。退出 0 仅表示该操作所列检查完成，2 表示输入、环境、转换或检查失败；中断不会被报告为成功。

## English

Prefer the project's chosen interpreter and configured tools. The optional pinned requirements cover DOCX, XLSX, and PDF parsing; each operation needs only its relevant dependencies. Install in an isolated environment only within existing authorization, outside skill resources and system Python. The helper downloads no tools and uses no remote conversion service.

The table and commands above define the shared interface. PDF export needs only the standard library and LibreOffice; existing-PDF rendering needs pypdf and pdftoppm, with LibreOffice added for Office inputs. Recalculation needs openpyxl and LibreOffice. DOCX/XLSX authoring libraries do not render or calculate formulas.

Use the selected Python and actual paths. Input is DOCX/XLSX/PPTX, plus PDF for render and only ordinary local XLSX for recalculation. Optional --pages selects comma-separated 1-based PDF pages; omission renders all pages. XLSX follows existing print layout, without sheet/range rendering. Tool flags select installed executables. The default 120-second timeout budgets the whole external command chain; timeout/interruption terminates and awaits owned processes without closing the user's existing Office session.

Output directories must be new. Original files, prior outputs, and user Office profiles remain intact. Artifacts are document.pdf, recalculated.xlsx, and pages/page-NNNN.png. The JSON report records source/output fingerprints, status, and checked scope; operation.log retains diagnostics. Preflight failures create no output; execution failures preserve artifacts and a failed report. visual_review remains not_run and is reported separately by an executor who actually inspected images.

PDF export does not implicitly render images or refresh caches. PNG signature checks do not establish readability/layout. Recalculation clears old caches in a temporary copy and requests full automatic calculation, preventing stale-cache passthrough; openpyxl staging does not guarantee advanced-feature fidelity. Recalculation rejects recognized external links/connections/macros/external-data formulas and does not accept array/data-table formula preservation; it is not external refresh or general Excel compatibility. Business logic, styles/advanced features, and native Office acceptance require task-specific checks. Exit 0 means only the listed checks completed; exit 2 means input, environment, conversion, or verification failure. Interruptions never count as success.
