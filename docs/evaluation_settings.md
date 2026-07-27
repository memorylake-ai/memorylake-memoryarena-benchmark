# 评测设置

在 MemoryArena 基准上评测 **MemoryLake** 时所用的设置。

## Agent 与 Judge

- 任务 Agent 模型：**GPT-5-mini**（通过 OpenAI 兼容 API 提供）。
- Judge 模型（对使用模型判分的任务）：**GPT-5-mini**。

## 任务、数据集与所选条目

评测覆盖 MemoryArena 五个任务。**除旅行规划取其中 30 组子集外，其余任务均为 test 集全量。**
各任务实际评测的条目 id 明细见 [`queries/`](queries/)：

| 任务 | 环境 / 数据集 | 实际评测规模 | 条目明细 |
|------|--------------|------------|----------|
| 形式化推理 · 数学 | HF `ZexueHe/memoryarena`，配置 `formal_reasoning_math`，`test` split | **40** 篇 paper（全量） | [`queries/formal_reasoning_math_ids.tsv`](queries/formal_reasoning_math_ids.tsv) |
| 形式化推理 · 物理 | HF `ZexueHe/memoryarena`，配置 `formal_reasoning_phys`，`test` split | **20** 篇 paper（全量） | [`queries/formal_reasoning_phys_ids.tsv`](queries/formal_reasoning_phys_ids.tsv) |
| 旅行规划 | 基于 TravelPlanner 的环境 | **30** 组（270 中的子集） | [`queries/travel_query_ids.tsv`](queries/travel_query_ids.tsv) |
| 网购 | 基于 WebShop 的环境 | **150** 个任务（5 类别 × 30，全量） | [`queries/shopping_task_ids.tsv`](queries/shopping_task_ids.tsv) |
| 网络搜索 | BrowseComp-Plus（渐进式） | **221** 条 query（全量） | [`queries/web_search_query_ids.tsv`](queries/web_search_query_ids.tsv) |

## 各任务说明

- **形式化推理（数学 / 物理）**：每条为一篇 paper，含**多个前后依赖的小问**（数学 3–11 问，物理 3–12 问），
  是多步 / 多会话的推理链。id 明细含 `paper_name` 与 `num_questions`。
- **网购**：5 个类别（`baking` / `beauty` / `electronics` / `grocery` / `home`），每类 30 个任务，
  每步上限 20；判分为**步骤精确匹配**（所选商品 ASIN）。
- **旅行规划**：从 TravelPlanner test 集（共 270 组）中取 **30 组**评测（id：1–18, 20, 22, 23, 25, 26, 28, 29, 30, 31, 32, 36, 38），均为多人物、多约束的行程规划场景，每条上限 30 步。
- **网络搜索**：**渐进式多子查询** —— 每条 query 拆成 **4–16 个子查询**（均值 7.4、中位 7）外加一个最终合并 query；
  检索 agent 在 BrowseComp-Plus 语料上工作：**top-k = 10** 段落、**每段截断 ≤ 512 token**、**最多 35 轮**；
  记忆在**每个子查询完成后写入一次**（渐进累积），最终合并 query 只读取记忆、不写入。

## 记忆（MemoryLake）设置

- 知识检索 **top-k = 10**。
- 按任务族的注入预算约束 `<memory_context>` 的大小。
- 网络搜索的轨迹综合（synthesis）：本次报告的实验中**关闭**。

## 判分

使用 MemoryArena 官方判分脚本：

- 形式化推理与网络搜索：**PS**（过程 / 逐步通过率）与 **SR**（最终成功率）；
- 旅行规划：**SPS / PS / SR**；网购：**step-match**（所选商品精确匹配）。
