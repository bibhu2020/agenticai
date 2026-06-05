# Microsoft AI Ecosystem

> Microsoft has rebranded products aggressively since 2023, creating a maze of overlapping "Copilot" and "Azure AI" names.  
> This document maps every major product: what it is today, what it used to be called, and where it fits.

---

## The "Copilot" Name Problem

Microsoft attached the **Copilot** brand to over a dozen distinct products. They are **not** the same product — they share a name and sometimes a UI shell, but they serve completely different audiences and purposes.

| Product Name | Audience | What It Actually Is | Old Name |
|---|---|---|---|
| **Microsoft Copilot** | General public | Consumer AI chat assistant (like ChatGPT). Available at copilot.microsoft.com, in Windows, in Edge. | Bing Chat (2023) |
| **Microsoft 365 Copilot** | Office users / Enterprise | AI woven into Word, Excel, PowerPoint, Outlook, Teams. Summarizes emails, drafts docs, analyzes spreadsheets. | — (new in 2023) |
| **GitHub Copilot** | Software developers | AI code completion and chat inside VS Code, JetBrains, Vim, etc. Autocompletes code, explains, reviews PRs. | — (launched 2021, predates the "Copilot" rebrand wave) |
| **Copilot Studio** | IT / Business app builders | Low-code/no-code platform to build custom AI chatbots and copilots. Can extend M365 Copilot or stand alone. | Power Virtual Agents |
| **Security Copilot** | Security analysts / SOC teams | AI for threat hunting, incident response, vulnerability analysis. Integrates with Sentinel, Defender, Intune. | — (new in 2023) |
| **Copilot in Power BI** | Data analysts | AI-generated data summaries, natural language querying of dashboards inside Power BI. | — |
| **Copilot in Fabric** | Data engineers | AI assistance inside Microsoft Fabric (data lakehouse platform). Generates Spark/SQL, explains pipelines. | — |
| **Dragon Copilot** | Healthcare workers | AI voice assistant for clinical documentation. Integrates with Epic, Cerner, other EHRs. | Dragon Medical / Nuance DAX |
| **Copilot+ PCs** | Consumers buying laptops | A hardware certification category for Windows PCs with an on-device NPU ≥ 40 TOPS. Not a software product. | — |
| **Copilot Vision** | General public (Edge) | Lets Copilot see and discuss your current browser tab. Experimental feature in Edge. | — |
| **Copilot Voice** | General public | Real-time voice conversation with Microsoft Copilot (similar to ChatGPT Advanced Voice). | — |
| **Microsoft Designer** | General public / Creatives | AI image and graphic design tool. Integrated into M365 and available standalone. | — |

> **Rule of thumb:** If "Copilot" is followed by a product name (M365 Copilot, Security Copilot), it's an AI layer bolted onto that product. The standalone "Microsoft Copilot" is just the consumer chatbot.

---

## The "Azure AI" Platform — Name Change History

Microsoft has renamed its developer and enterprise AI platform multiple times, and the old names still appear in documentation.

```
Timeline of the developer platform:
  Azure Machine Learning Studio  (2014–2021)
          ↓
  Azure ML + Azure Cognitive Services  (separate products, 2018–2023)
          ↓
  Azure AI Studio  (unified portal, early 2024)
          ↓
  Azure AI Foundry  (renamed late 2024 — current name)
```

### Azure AI Foundry (Current — the developer hub)

[Azure AI Foundry](https://ai.azure.com) is Microsoft's **unified AI development platform**. One portal where you:
- Browse and deploy 1,700+ models (OpenAI, Meta Llama, Mistral, Phi, Cohere, etc.)
- Build, test, and evaluate prompts and agents (Prompt Flow)
- Fine-tune models
- Monitor production AI apps for safety and quality

| Old Name | New Name | Notes |
|---|---|---|
| Azure AI Studio | Azure AI Foundry | Renamed late 2024. Same URL (ai.azure.com). All docs migrated. |
| Azure Cognitive Services | Azure AI Services | Umbrella for all pre-built AI APIs (Vision, Speech, Language, etc.) |
| Azure Cognitive Search | Azure AI Search | Now supports vector search and hybrid (keyword + semantic) search |
| Form Recognizer | Azure AI Document Intelligence | Extracts structured data from documents, invoices, receipts |
| Text Analytics | Azure AI Language | NLP: sentiment, entity extraction, summarization, PII detection |
| Computer Vision | Azure AI Vision | Image analysis, OCR, face detection, spatial analysis |
| LUIS (Language Understanding) | Merged into Azure AI Language | Conversational NLP — no longer a standalone product |
| QnA Maker | Merged into Azure AI Language (Custom Question Answering) | Knowledge-base Q&A |
| Power Virtual Agents | Copilot Studio | Low-code bot/copilot builder |

---

## Models Microsoft Owns or Controls

Microsoft is unusual in that it ships its own models **and** has deep integration with OpenAI's models.

### Microsoft's Own Models

| Model Family | Details | Best Use |
|---|---|---|
| **Phi-4** | Small language model (14B). Trained on synthetic data. Surprisingly capable at reasoning and coding for its size. | On-device use, edge deployment, cost-efficient apps |
| **Phi-4-mini** | Compact version (~3.8B). Runs on CPU and mobile NPUs. | Mobile apps, Copilot+ PC on-device features |
| **MAI-1** | Larger proprietary model (~500B parameters, 2024). Less publicly documented. | Potential backbone for future Copilot features |
| **Florence** | Microsoft's vision foundation model. Powers many Azure AI Vision features. | Image classification, captioning, OCR, grounding |

### OpenAI Models (via Partnership)

Microsoft is OpenAI's largest investor and exclusive cloud partner. You access OpenAI models through Microsoft via:

| Access Point | What You Get |
|---|---|
| **Azure OpenAI Service** | GPT-4o, GPT-4o-mini, o1, o3, o4-mini, GPT-4 Turbo, Whisper, DALL·E 3, text-embedding models — all on Azure infrastructure with enterprise compliance |
| **Microsoft Copilot (consumer)** | Powered by GPT-4o and o-series behind the scenes |
| **GitHub Copilot** | GPT-4o for chat; o3 for reasoning tasks |

> **Key distinction:** Azure OpenAI Service is not the same as calling api.openai.com. Azure gives you private endpoints, VNET integration, content filtering, compliance certifications (SOC 2, HIPAA), and regional data residency guarantees.

---

## Developer Platforms & APIs

### Azure OpenAI Service

- **What:** Managed API access to OpenAI's frontier models, hosted in Azure data centers.
- **Who:** Developers and enterprises who need OpenAI models with enterprise SLAs, data privacy, and compliance.
- **Key features:** Private endpoints, customer-managed keys, content filters, usage quotas, regional deployment (US, EU, Asia).
- **vs. OpenAI API directly:** Azure adds compliance/security; direct OpenAI is simpler for startups.

### Azure AI Foundry (developer perspective)

- **Model catalog** — discover and compare models from OpenAI, Meta, Mistral, Cohere, Phi, and others.
- **Prompt Flow** — visual workflow builder for LLM chains, RAG pipelines, evaluation runs.
- **Fine-tuning** — supervised fine-tuning for GPT-4o, Phi, and other models.
- **Evaluation** — built-in metrics for groundedness, coherence, safety, relevance.
- **Azure AI Inference SDK** — unified Python/JS SDK to call any model in the catalog with one client.

```python
# Azure AI Inference SDK — works with any model in the Foundry catalog
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint="https://<your-project>.services.ai.azure.com/models",
    credential=AzureKeyCredential("<key>"),
)
response = client.complete(
    model="gpt-4o",           # swap to "Phi-4", "Llama-3.3-70B-Instruct", etc.
    messages=[{"role": "user", "content": "Explain vector search"}],
)
```

### Azure AI Services (pre-built APIs)

Ready-to-use AI APIs — no model training required. Just call the REST endpoint.

| Service | What It Does |
|---|---|
| **Azure AI Language** | Sentiment analysis, NER, summarization, PII detection, translation, key phrase extraction |
| **Azure AI Vision** | Image analysis, OCR, face detection, product recognition, spatial analysis |
| **Azure AI Speech** | Speech-to-text, text-to-speech, speaker recognition, real-time translation |
| **Azure AI Translator** | 100+ language translation; document translation |
| **Azure AI Document Intelligence** | Extract tables, key-value pairs, signatures from PDFs, invoices, receipts, IDs |
| **Azure AI Content Safety** | Detect hate, violence, sexual content, self-harm in text and images |
| **Azure AI Search** | Hybrid search (keyword + vector + semantic re-ranking) over your data |
| **Azure AI Bot Service** | Managed hosting for chatbots built with the Bot Framework |

---

## Agentic Frameworks

Microsoft owns two major open-source agent frameworks and integrates them into Azure AI Foundry.

### AutoGen

[AutoGen](https://microsoft.github.io/autogen/stable/) — multi-agent conversation framework.

- **Concept:** Agents are conversational actors. You define agents (each with a role, LLM, tools), group them, and let them debate/collaborate to solve problems.
- **Key patterns:** Two-agent chat, group chat, nested chats, human-in-the-loop, tool/function calling.
- **AutoGen Studio** — no-code UI to build AutoGen workflows visually.
- **v0.4+** — rewritten with async-first `AgentChat` API. The old v0.2 API is still widely documented online but deprecated.

```python
# AutoGen v0.4 — simple two-agent coding example
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

model_client = AzureOpenAIChatCompletionClient(model="gpt-4o", ...)

coder = AssistantAgent("coder", model_client=model_client,
                       system_message="You write Python code.")
reviewer = AssistantAgent("reviewer", model_client=model_client,
                          system_message="You review code for bugs.")

team = RoundRobinGroupChat([coder, reviewer], max_turns=4)
```

- **Best for:** Complex multi-agent workflows where agents need to argue, verify, or decompose tasks.

### Semantic Kernel

[Semantic Kernel](https://learn.microsoft.com/semantic-kernel) — AI orchestration SDK for production apps.

- **Concept:** Plug-and-play SDK that wraps LLMs as a "kernel." You add plugins (tools/functions), memory, and planners; the kernel routes calls intelligently.
- **Languages:** Python, C# (primary), Java.
- **Key components:**
  - **Kernel** — the central orchestrator; holds LLM + plugins.
  - **Plugins** — groups of native functions or OpenAI-format functions the LLM can call.
  - **Planner** — auto-generates a plan (sequence of plugin calls) to fulfill a user goal.
  - **Memory / Vector Store** — built-in connectors for Azure AI Search, Chroma, Qdrant, etc.
  - **Process Framework** — structured workflow engine for multi-step business processes.
  - **Agent Framework** — `ChatCompletionAgent`, `OpenAIAssistantAgent` wrappers.

```python
# Semantic Kernel — basic plugin and kernel setup
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function

kernel = Kernel()
kernel.add_service(AzureChatCompletion(deployment_name="gpt-4o", ...))

class MathPlugin:
    @kernel_function(description="Adds two numbers")
    def add(self, a: float, b: float) -> float:
        return a + b

kernel.add_plugin(MathPlugin(), "math")
```

- **Best for:** Enterprise .NET/Python apps that need structured AI orchestration with governance, memory, and process management.

### AutoGen vs. Semantic Kernel — When to Use Which

| | AutoGen | Semantic Kernel |
|---|---|---|
| **Style** | Conversational multi-agent | Plugin/function orchestration |
| **Language focus** | Python-first | C# primary, Python strong |
| **Best pattern** | Agents debating/collaborating | Structured app + LLM workflows |
| **Enterprise readiness** | Improving (v0.4+) | Production-ready, Microsoft-backed |
| **No-code option** | AutoGen Studio | Copilot Studio |

> They are **complementary**, not competing. Semantic Kernel can orchestrate AutoGen agents. Azure AI Foundry integrates both.

---

## IDE & Developer Coding Tools

| Tool | What It Is | How It Relates to Microsoft |
|---|---|---|
| **GitHub Copilot** | AI code completion and chat inside VS Code, JetBrains, Vim, Xcode, etc. | Microsoft owns GitHub (acquired 2018). Copilot is the flagship developer AI product. Uses GPT-4o and o-series. |
| **GitHub Copilot Workspace** | AI agent that takes a GitHub Issue and plans + writes the code changes end-to-end. | Agentic extension of Copilot. Still in preview. |
| **GitHub Copilot Extensions** | Let third-party tools (DataStax, Docker, Sentry) plug into Copilot chat. | Open ecosystem for Copilot. |
| **GitHub Models** | Free playground to test 30+ models (GPT, Llama, Mistral, Phi) inside GitHub. | Uses Azure AI Foundry model catalog under the hood. |
| **VS Code** | Microsoft's code editor. Has built-in Copilot Chat panel. | The primary editor; Copilot is deeply integrated. |
| **Azure Developer CLI (`azd`)** | CLI to scaffold and deploy Azure GenAI apps from templates. | Accelerates the "code to Azure" workflow. |

### GitHub Copilot Tiers (as of 2025)

| Tier | Price | Key Features |
|---|---|---|
| **Free** | $0 | 2,000 completions/month, 50 chat messages/month, Claude 3.5 Sonnet + GPT-4o |
| **Pro** | $10/month | Unlimited completions, all models, Claude Sonnet, Gemini Flash |
| **Pro+** | $39/month | All models including o3, Claude 3.7 Sonnet, unlimited Copilot agents |
| **Business** | $19/user/month | Org policy controls, audit logs, IP indemnity |
| **Enterprise** | $39/user/month | Fine-tuning on org code, Copilot Workspace, advanced security |

---

## Machine Learning Platform — Azure Machine Learning

[Azure Machine Learning](https://azure.microsoft.com/products/machine-learning) is Microsoft's full ML lifecycle platform (distinct from the GenAI-focused AI Foundry, though they share infrastructure).

| Capability | Description |
|---|---|
| **Compute clusters** | Managed GPU/CPU clusters for training jobs; autoscale to zero. |
| **Managed online endpoints** | Deploy models as REST APIs with autoscaling and blue/green deployments. |
| **Pipelines** | DAG-based ML pipelines for reproducible training workflows. |
| **AutoML** | Automated model selection and hyperparameter tuning for classification, regression, forecasting, NLP, CV. |
| **MLflow integration** | Track experiments, log metrics, register models. Azure ML is an MLflow server. |
| **Model registry** | Versioned model storage with lineage tracking. |
| **Responsible AI dashboard** | Explainability (SHAP), fairness assessment, error analysis, counterfactuals. |
| **Feature Store** | Centralized feature definitions and offline/online serving. |
| **Prompt Flow** | Also available in Azure ML for LLM pipeline development and evaluation. |

> **Azure ML vs. Azure AI Foundry:** Azure ML is for classical ML and custom model training. AI Foundry is for building GenAI apps using foundation models. They share the Azure portal but serve different workflows. Both are converging in the Azure AI Foundry umbrella.

---

## Data & Analytics — Microsoft Fabric

[Microsoft Fabric](https://fabric.microsoft.com) is Microsoft's unified data platform (launched 2023), replacing/unifying Power BI, Azure Synapse, Azure Data Factory, and Azure Data Lake.

| Component | Old Product | What It Does |
|---|---|---|
| **OneLake** | Azure Data Lake Gen2 | Single data lake for the whole organization; Delta Parquet format. |
| **Data Factory** | Azure Data Factory | Data ingestion and ETL pipelines. |
| **Synapse Data Engineering** | Azure Synapse Analytics | Spark notebooks and lakehouse compute. |
| **Synapse Data Warehouse** | Azure Synapse SQL | Serverless SQL over OneLake. |
| **Power BI** | Power BI | BI dashboards and reports. Now embedded in Fabric. |
| **Real-Time Intelligence** | Azure Stream Analytics | Streaming data and event-based analytics. |
| **Copilot in Fabric** | — | AI that writes Spark/SQL code, explains results, generates reports. |

---

## Enterprise Productivity — Microsoft 365 Copilot in Detail

M365 Copilot is NOT one feature — it's a layer of AI across every Office app. Each app gets different capabilities.

| App | What Copilot Does |
|---|---|
| **Outlook** | Summarizes email threads, drafts replies, schedules meetings, surfaces action items. |
| **Teams** | Transcribes meetings live, generates summaries and action items, answers "what did I miss?" |
| **Word** | Drafts documents from a prompt, rewrites/shortens sections, summarizes attached docs. |
| **Excel** | Generates formulas, creates charts from natural language, identifies trends, runs analysis. |
| **PowerPoint** | Creates full slide decks from Word docs or prompts; adds speaker notes. |
| **OneNote** | Summarizes notes, generates plans, answers questions about your notebooks. |
| **Loop** | Collaborative AI workspace; generates content inline across Loop pages. |
| **SharePoint** | Summarizes sites and documents; integrated with Copilot pages. |
| **Viva** | HR-focused: coaching, skill tracking, meeting analytics (Viva Insights, Viva Learning). |

### Copilot Pages

A new canvas in M365 Copilot (2024) where Copilot outputs become editable, shareable documents — essentially AI-generated artifacts that persist in OneDrive and can be shared as Loop components.

---

## Windows AI Features

| Feature | What It Does | Status |
|---|---|---|
| **Recall** | Captures periodic screenshots of everything you do on your PC. Lets you search your "timeline" with natural language. | Controversial (privacy). Rolling out to Copilot+ PCs. Opt-in. |
| **Click to Do** | Right-click anything on screen to get AI actions (summarize, translate, rewrite, web search). | Copilot+ PCs only. |
| **Cocreator (Paint)** | Real-time AI image generation inside Windows Paint as you draw. | Copilot+ PCs only. |
| **Live Captions with translation** | Real-time translation of any audio on your PC into English captions. | Available now. |
| **Windows Copilot Runtime** | The on-device AI framework; manages the NPU, runs Phi Silica (distilled Phi model) locally. | Powers all on-device Copilot+ features. |
| **Phi Silica** | A distilled Phi model that runs entirely on-device (NPU). No internet needed. | Copilot+ PCs only. |

---

## Power Platform (Low-Code / No-Code AI)

| Product | Old Name | What It Does |
|---|---|---|
| **Power Apps** | — | Low-code app builder. Copilot can generate apps from natural language descriptions. |
| **Power Automate** | Microsoft Flow | Workflow automation. AI Builder adds document processing and prediction. |
| **Power BI** | — | BI and dashboards. Copilot generates insights and report narrative. |
| **Copilot Studio** | Power Virtual Agents | Build and publish custom AI chatbots (copilots). No-code + pro-code. Integrates with M365 Copilot. |
| **AI Builder** | — | Pre-built AI models in Power Platform: object detection, form processing, sentiment, prediction. |

### Copilot Studio vs. AutoGen vs. Azure AI Foundry Agents

| | Copilot Studio | AutoGen | Azure AI Foundry Agents |
|---|---|---|---|
| **Audience** | Business users / citizen developers | AI engineers | Pro developers |
| **Code required** | No (visual) | Yes (Python) | Yes (Python/REST) |
| **Best for** | Customer service bots, M365 Copilot extensions | Multi-agent research/task workflows | Production API agents |
| **Integration** | M365, Teams, SharePoint, Power Platform | Any Python environment | Azure services, APIs |

---

## Security AI Products

| Product | What It Does |
|---|---|
| **Microsoft Security Copilot** | Natural language interface for security analysts. Ask questions about incidents, get threat intelligence, write KQL queries, triage alerts. Integrates with Sentinel, Defender, Entra, Purview, Intune. |
| **Microsoft Defender (AI features)** | Automatic attack disruption — AI detects and contains attacks in progress (e.g., ransomware) without waiting for human response. |
| **Microsoft Sentinel (AI features)** | SIEM with AI-driven incident correlation, UEBA (user behavior analytics), AI-generated investigation summaries. |
| **Microsoft Purview (AI governance)** | Data loss prevention, compliance, and now AI governance — tracks what data your AI apps are accessing. |
| **Entra ID (AI features)** | AI-driven conditional access risk scoring; detects anomalous sign-in patterns. |

---

## Full Product Map by Audience

### General Users

| Product | Purpose |
|---|---|
| Microsoft Copilot (copilot.microsoft.com) | Consumer AI chat; free, in Windows and Edge |
| Microsoft 365 Copilot | AI in Word, Excel, PowerPoint, Outlook, Teams |
| Microsoft Designer | AI image and graphic creation |
| Copilot in Bing | Web search with AI answers (now just "Microsoft Copilot" in Bing) |
| Windows Recall / Click to Do | On-PC AI features (Copilot+ PCs) |

### Developers Building GenAI Apps

| Product | Purpose |
|---|---|
| Azure AI Foundry | Unified portal: model catalog, Prompt Flow, evaluation, fine-tuning |
| Azure OpenAI Service | Enterprise-grade access to GPT-4o, o-series, Whisper, DALL·E |
| Azure AI Services | Pre-built AI APIs: Language, Vision, Speech, Document Intelligence, Search |
| Azure AI Inference SDK | Unified Python/JS SDK for all Foundry models |
| Semantic Kernel | AI orchestration SDK for building structured LLM apps |
| AutoGen | Multi-agent framework for complex collaborative agent workflows |
| GitHub Models | Free playground to test and prototype with 30+ models |

### ML Engineers / Data Scientists

| Product | Purpose |
|---|---|
| Azure Machine Learning | Full MLOps: training, AutoML, pipelines, model registry, deployment |
| Microsoft Fabric | Unified data lakehouse: Spark, SQL, Data Factory, Power BI |
| Azure AI Search | Hybrid/vector search over custom data |
| Responsible AI Dashboard | Explainability, fairness, error analysis for ML models |

### Enterprise IT / Business

| Product | Purpose |
|---|---|
| Copilot Studio | Build custom copilots for internal/external use; no-code |
| Security Copilot | AI for the SOC — threat hunting, incident triage, KQL generation |
| Microsoft Purview AI | Governance and compliance for AI usage across the org |
| Power Platform (AI Builder) | AI features in Power Apps and Power Automate |
| Azure Arc | Extend Azure governance to on-prem and multi-cloud AI workloads |

---

## Key Relationships to Understand

```
Microsoft
├── Owns GitHub → GitHub Copilot (developer coding AI)
├── Invested in / Partners with OpenAI → Azure OpenAI Service
│                                      → Microsoft Copilot (uses GPT-4o)
│                                      → M365 Copilot (uses GPT-4o)
├── Acquired Nuance (2022) → Dragon Copilot (healthcare)
├── Acquired LinkedIn → LinkedIn AI features (job coaching, post writing)
└── Own models: Phi-4, Florence, MAI-1
```

```
"Azure AI" umbrella (as of 2025):
├── Azure AI Foundry         ← developer hub (was Azure AI Studio)
│   ├── Model Catalog        ← 1700+ models
│   ├── Prompt Flow          ← LLM pipeline builder
│   ├── Evaluations          ← quality/safety scoring
│   └── Agent Service        ← managed agent hosting
├── Azure OpenAI Service     ← OpenAI models with enterprise compliance
├── Azure AI Services        ← pre-built APIs (was Cognitive Services)
│   ├── AI Language          (was Text Analytics + LUIS + QnA Maker)
│   ├── AI Vision            (was Computer Vision)
│   ├── AI Speech
│   ├── AI Document Intelligence  (was Form Recognizer)
│   ├── AI Search            (was Cognitive Search)
│   └── AI Content Safety
└── Azure Machine Learning   ← ML training, MLOps, AutoML
```
