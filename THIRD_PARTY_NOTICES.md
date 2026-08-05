# Third-party notices

This repository is licensed under Apache-2.0 (see [`LICENSE`](LICENSE)). **That license covers
only the files in this repository.** It does not, and cannot, extend to any third-party code
referenced from here.

## `third_party/MemoryArena` — referenced, not redistributed

The benchmark implementation is referenced as a **git submodule**, so this repository stores
only a URL and a commit id — no upstream source is copied into it or redistributed under
Apache-2.0.

| | |
|---|---|
| Referenced at | `third_party/MemoryArena` |
| Submodule URL | <https://github.com/memorylake-ai/MemoryArena> |
| Pinned commit | `6cd9de14b71915e39ac742a20dc33785e14b6aab` |
| Origin | fork of <https://github.com/ZexueHe/MemoryArena> |
| Paper | MemoryArena, [arXiv:2602.16313](https://arxiv.org/abs/2602.16313) |

> ⚠️ **The upstream repository publishes no license.** As of the pinned commit,
> `ZexueHe/MemoryArena` contains no `LICENSE`, `COPYING` or `NOTICE` file, and GitHub reports
> its license as `NOASSERTION`. Absent an explicit grant, the default position under copyright
> law is that all rights are reserved by its authors: publication on a public repository is not
> itself a license to copy, modify, redistribute or use the code beyond what the
> [GitHub Terms of Service](https://docs.github.com/site-policy/github-terms/github-terms-of-service)
> allow for public repositories (viewing and forking within GitHub).
>
> This repository therefore **links** to the code rather than vendoring it, and the fork is
> kept public on GitHub with no license file added — neither this project nor the fork asserts
> any license over upstream's work. Anyone intending to use the benchmark code beyond viewing
> and forking on GitHub should seek an explicit license from its authors.

## Components bundled inside MemoryArena

MemoryArena aggregates several third-party projects. Their own terms govern those parts, and
they are listed here for attribution because the pinned upstream tree does not carry their
license texts (only `memory/memory_systems/MemoRAG/LICENSE` is present):

| Component in MemoryArena | Upstream project | License |
|---|---|---|
| `env/env_systems/travel_planner_env` | [OSU-NLP-Group/TravelPlanner](https://github.com/OSU-NLP-Group/TravelPlanner) | MIT |
| `env/env_systems/web_shopping_env` | [princeton-nlp/WebShop](https://github.com/princeton-nlp/WebShop) | MIT |
| `env/env_systems/web_search_env` (parts) | [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch) | Apache-2.0 |
| calibration-error routine in `evaluate_with_openai.py` | [hendrycks/outlier-exposure](https://github.com/hendrycks/outlier-exposure) | Apache-2.0 |
| `memory/memory_systems/MemoRAG` | MemoRAG | Apache-2.0 (license text included upstream) |
| `MemActBench` (declared submodule) | [wangyu-ustc/MemActBench](https://github.com/wangyu-ustc/MemActBench) | unknown — repository not publicly reachable |

## Datasets

Task data are obtained from the HuggingFace dataset `ZexueHe/memoryarena` and the upstream
sources it derives from (TravelPlanner, WebShop, BrowseComp-Plus). Dataset terms are those of
their respective publishers and are not granted by this repository.

## Checking out the reference

`MemoryArena` declares a submodule (`MemActBench`) whose repository is **not publicly
reachable**, so a recursive clone fails. Clone non-recursively:

```bash
git clone https://github.com/memorylake-ai/memorylake-memoryarena-benchmark
cd memorylake-memoryarena-benchmark
git submodule update --init third_party/MemoryArena   # NOT --recursive
```
