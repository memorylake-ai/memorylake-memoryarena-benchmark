# MemoryLake 方法简介

**MemoryLake** 是我们在 MemoryArena 基准上评测的记忆系统。它是一套**双轨（dual-track）**记忆，
把"实例知识"与"可复用过程"分开处理，并通过标准适配器接口
（`add_chunk(chunk)` / `wrap_user_prompt(question)`，按 `user_id` 隔离）接入 MemoryArena
——与其它记忆基线完全一致。

## 双轨设计

- **DOC 轨（按用户 / 会话）。** 每一段 agent 轨迹（chunk）都写入该用户的知识库，并组织成两个互补视图：
  - **QA 视图** —— 后续步骤可复用的**已解出**的事实 / 结论；
  - **PROCESS 视图** —— 结论是**如何**得到的（过程）。

  查询时对两个视图分别做 top-k 检索，注入到一个受预算约束的 `<memory_context>` 中。
  DOC 轨由 MemoryLake 的知识 / 检索服务支撑。

- **SKILL 轨（按任务族，全局共享）。** 从已完成的轨迹里蒸馏出简短、**去实例化**的**可复用过程**（"技能"）
  —— 即某一类任务的关键步骤 + 容易踩的坑。技能经去重后汇成一个精简库，仅在当前任务与之相关时才注入。

## 召回与注入

在 `wrap_user_prompt` 时，MemoryLake 把两条轨的召回合并成单个 `<memory_context>` 块，
并受**按任务族的 token 预算**约束，保证记忆不会挤占任务本身的 prompt。
所有 LLM 调用（蒸馏、检索整理、judge）都使用同一个任务模型。

> 本目录仅记录**评测设置**；MemoryLake 的实现单独维护，不包含在此贡献中。
