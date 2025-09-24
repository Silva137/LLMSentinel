# LLMSentinel

**LLMSentinel** is a comprehensive web platform, developed as part of a Master's thesis project, for benchmarking Large Language Models (LLMs) on specific cybersecurity tasks. The platform enables researchers, students, and professionals to evaluate, compare, and analyze the performance of multiple LLMs from different providers in a unified and intuitive environment.

---

## Key Features
- **Unified access to multiple LLMs**: Integration with [OpenRouter](https://openrouter.ai/) to standardise communication with models from different providers (OpenAI, Anthropic, Google, Mistral, etc.)
- **Integrated Benchmarks:** Includes a suite of reference benchmarks like **SecQA**, **CSLU**, datasets from **CyberBench**, and a newly developed benchmark, **CyberDomain**, which covers 7 fundamental cybersecurity areas.
- **Automated evaluation**:
  - Multiple-choice question answering (MMLU style)
  - Metrics: Accuracy, Response time, Confidence intervals
- **Collaborative dataset management**: Import CSV datasets and share them with the community
- **Web interface**: Authentication, intuitive dashboards, comparative results with tables & charts

---

## 🛠️ Tech Stack
- **Frontend:** Typescript + React
- **Backend:** Python + Django
- **Database:** PostgreSQL  
- **LLM Communication:** OpenRouter API.

---

## 📸 Screenshots
See [Annex: Final UI](docs/annex_interface_final.md) for full screenshots of the platform.

Jump straight to specific sections:

- [Login page](docs/annex_interface_final.md#p%C3%A1gina-de-autentica%C3%A7%C3%A3o-login)
- [User registration](docs/annex_interface_final.md#p%C3%A1gina-de-registo-de-novos-utilizadores)
- [API key setup (OpenRouter) modal](docs/annex_interface_final.md#pop-up-configura%C3%A7%C3%A3o-de-chave-de-api-openrouter)
- [Models page (listing & search)](docs/annex_interface_final.md#p%C3%A1gina-de-modelos-listagem--pesquisa)
- [Datasets page](docs/annex_interface_final.md#p%C3%A1gina-de-datasets)
- [Dataset details](docs/annex_interface_final.md#detalhe-de-um-dataset)
- [Import datasets (CSV) modal](docs/annex_interface_final.md#pop-up-importa%C3%A7%C3%A3o-de-datasets-csv)
- [Community datasets](docs/annex_interface_final.md#p%C3%A1gina-de-datasets-comunit%C3%A1rios)
- [Evaluations page](docs/annex_interface_final.md#p%C3%A1gina-de-avalia%C3%A7%C3%B5es-executadas)
- [New evaluation (dataset & model selection) modal](docs/annex_interface_final.md#pop-up-nova-avalia%C3%A7%C3%A3o-sele%C3%A7%C3%A3o-de-dataset-e-modelo)
- [Evaluation details](docs/annex_interface_final.md#detalhes-de-uma-avalia%C3%A7%C3%A3o)
- [Comparative charts (Overview)](docs/annex_interface_final.md#gr%C3%A1ficos-comparativos-overview)

<p align="center">
  <img src="docs/screenshots/login_page.png" alt="Login" width="360" />
  <img src="docs/screenshots/models_page.png" alt="Models" width="360" />
  <img src="docs/screenshots/overview_page.png" alt="Overview" width="360" />
</p>
---

## 🌐 Deployment

The **LLMSentinel** platform is live at:  
**https://frontend-rnow.onrender.com**

> Note: the first load may take a few seconds due to cold start on the hosting provider.