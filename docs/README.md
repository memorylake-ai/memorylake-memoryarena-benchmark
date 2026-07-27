# MemoryLake 在 MemoryArena 上的评测设置

本目录记录 **MemoryLake 在 MemoryArena 基准上的评测方式**：所用数据集与条目选取、
Agent / 记忆 / Judge 的配置，以及一份简短的方法说明。

**范围：** 仅设置与文档。MemoryLake 的实现不包含在此贡献中。

## 目录内容

- [`method.md`](method.md) —— MemoryLake 记忆系统简介（双轨：DOC + SKILL）。
- [`evaluation_settings.md`](evaluation_settings.md) —— 各任务的数据集、所选条目与超参数。
- [`queries/`](queries/) —— 各任务实际评测的条目 id 明细：
  - [`formal_reasoning_math_ids.tsv`](queries/formal_reasoning_math_ids.tsv) —— 数学 40 篇（`id`, `paper_name`, `num_questions`）
  - [`formal_reasoning_phys_ids.tsv`](queries/formal_reasoning_phys_ids.tsv) —— 物理 20 篇
  - [`travel_query_ids.tsv`](queries/travel_query_ids.tsv) —— 旅行 **30** 组（`id`；270 中的子集）
  - [`shopping_task_ids.tsv`](queries/shopping_task_ids.tsv) —— 网购 150 个（`category`, `task_file`）
  - [`web_search_query_ids.tsv`](queries/web_search_query_ids.tsv) —— 网络搜索 221 条（`query_id`, `num_subqueries`）
