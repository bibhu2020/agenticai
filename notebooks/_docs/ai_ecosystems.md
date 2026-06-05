# AI Ecosystem Overview

> Organized by use-case audience: **General Users**, **Developers building GenAI apps**, and **Data Scientists / ML Engineers**.

---

## 1. Chat Tools (General Users)

Consumer-facing AI assistants for everyday questions, coding help, writing, research, and more.

| Product | Company | Free Tier | Notable Strengths | Best For |
|---|---|---|---|---|
| [ChatGPT](https://chat.openai.com) | OpenAI | Yes (GPT-4o mini) | Huge ecosystem, plugins, image gen, voice, web search | General purpose; widest feature set |
| [Claude.ai](https://claude.ai) | Anthropic | Yes (Sonnet) | Long context, nuanced reasoning, coding, safety | Writing, analysis, coding, long docs |
| [Gemini](https://gemini.google.com) | Google | Yes (Flash) | Deep Google Workspace integration, multimodal, real-time search | Research, productivity, Google users |
| [Microsoft Copilot](https://copilot.microsoft.com) | Microsoft | Yes | M365 integration, Bing search, enterprise features | Office users, enterprise workflows |
| [Grok](https://grok.com) | xAI (Elon Musk) | Yes (limited) | Real-time X/Twitter data, less restricted, image gen | Current events, uncensored queries |
| [Perplexity AI](https://perplexity.ai) | Perplexity | Yes | Search-first with citations, always up-to-date | Research with source attribution |
| [Meta AI](https://meta.ai) | Meta | Yes | Embedded in WhatsApp, Instagram, Facebook, Messenger | Social platform assistant |
| [Apple Intelligence / Siri](https://apple.com/apple-intelligence) | Apple | Yes (on-device) | Privacy-first, on-device processing, OS integration | iPhone/Mac users, privacy-sensitive use |
| [Gemini Live](https://gemini.google.com) | Google | Paid (Advanced) | Real-time voice conversation, camera awareness | Voice-first, real-time interaction |
| [NotebookLM](https://notebooklm.google.com) | Google | Yes | Deep document analysis, podcast generation from sources | Research synthesis, document Q&A |

---

## 2. Foundation Models

Models that power AI applications. Developers access these through APIs; some are open-source.

### Closed / Proprietary Models

| Model Family | Company | Top Models (as of 2025) | Context Window | Strengths |
|---|---|---|---|---|
| GPT-4o / o-series | OpenAI | GPT-4o, o1, o3, o4-mini, GPT-5 | Up to 128K | Reasoning (o-series), multimodal, code |
| Claude | Anthropic | Claude 4 Opus, Claude 4 Sonnet, Claude 3.5 Haiku | Up to 200K | Long context, coding, analysis, safety |
| Gemini | Google | Gemini 2.5 Pro, 2.5 Flash, 2.0 Flash | Up to 1M (Flash) | Multimodal, long context, speed/cost tradeoff |
| Grok | xAI | Grok 3, Grok 3 Mini | 131K | Real-time data, reasoning, open approach |
| Nova / Titan | Amazon | Nova Micro/Lite/Pro, Titan Embeddings | Up to 300K | Cost-efficient, AWS-native, multimodal |
| MAI / Phi | Microsoft | Phi-4, Phi-4-mini | Up to 128K | Small but capable, on-device use |
| Mistral | Mistral AI | Mistral Large 2, Mistral Small 3 | Up to 128K | European privacy compliance, efficiency |

### Open / Open-Weight Models

| Model Family | Company | Top Models | Strengths |
|---|---|---|---|
| Llama | Meta | Llama 4 Scout, Llama 4 Maverick, Llama 3.3 70B | Best open-weight; runs locally |
| Gemma | Google | Gemma 3 (1B–27B) | Lightweight, efficient, runs on edge |
| Mistral | Mistral AI | Mixtral 8x22B, Mistral 7B | Strong at instruction-following; MoE architecture |
| Phi | Microsoft | Phi-4 mini | Small models, surprisingly capable |
| Qwen | Alibaba | Qwen 2.5, QwQ-32B | Strong multilingual, coding |
| DeepSeek | DeepSeek | DeepSeek V3, R1 | Reasoning-focused, MIT license |

> **Where to find/run open models:** [Hugging Face](https://huggingface.co), [Ollama](https://ollama.ai) (local), [Together AI](https://together.ai), [Groq](https://groq.com) (fast inference), [Replicate](https://replicate.com)

---

## 3. Developer APIs & Platforms (Building GenAI Applications)

Platforms and APIs developers use to integrate AI into their own products.

### Model Access APIs

| Platform | Company | Models Available | Key Features | Best For |
|---|---|---|---|---|
| [OpenAI API](https://platform.openai.com) | OpenAI | GPT-4o, o-series, Codex, DALL·E, Whisper | Assistants API, Realtime API, fine-tuning, batch | All-in-one GenAI app development |
| [Anthropic API](https://docs.anthropic.com) | Anthropic | Claude 4 Opus/Sonnet/Haiku | Prompt caching, extended thinking, tool use, MCP | Safety-focused, long-context apps |
| [Google AI Studio](https://aistudio.google.com) | Google | Gemini 2.5 Pro/Flash, Gemma | Free prototyping, multimodal, grounding, code execution | Fast prototyping, learning |
| [Vertex AI](https://cloud.google.com/vertex-ai) | Google | Gemini, Llama, Mistral, + 3rd party | Enterprise MLOps, model registry, evaluation, RAG engine | Production enterprise GenAI |
| [Azure OpenAI Service](https://azure.microsoft.com/ai-services/openai) | Microsoft | GPT-4o, o-series, Whisper, DALL·E | Private deployment, enterprise SLAs, compliance | Enterprise OpenAI with Azure security |
| [Azure AI Foundry](https://ai.azure.com) | Microsoft | 1700+ models (OpenAI, Meta, Mistral, etc.) | Unified AI platform, prompt flow, fine-tuning, evals | Multi-model enterprise apps |
| [Amazon Bedrock](https://aws.amazon.com/bedrock) | Amazon | Nova, Claude, Llama, Mistral, Titan | Serverless AI, guardrails, RAG (Knowledge Bases) | AWS-native GenAI apps |
| [Groq](https://groq.com) | Groq | Llama 4, Gemma, Mistral, Qwen | Extremely fast inference (LPU chips), low latency | Real-time, speed-critical apps |
| [Together AI](https://together.ai) | Together AI | 50+ open models | Fine-tuning, fast inference, open model focus | Open-source model deployment |
| [Hugging Face Inference](https://huggingface.co/inference-api) | Hugging Face | 500K+ open models | Model hub, datasets, Spaces apps, AutoTrain | Open model research and deployment |

### Key Developer SDKs

| SDK | Language | Provider | Purpose |
|---|---|---|---|
| `openai` Python/JS SDK | Python, JS/TS | OpenAI | Access GPT, embeddings, images, audio, agents |
| `anthropic` Python/JS SDK | Python, JS/TS | Anthropic | Access Claude models, streaming, tool use |
| `google-genai` SDK | Python, JS | Google | Access Gemini via AI Studio or Vertex |
| `boto3` / AWS SDK | Python | Amazon | Access Bedrock, SageMaker |
| `azure-ai-inference` | Python | Microsoft | Access Azure AI Foundry models |
| `langchain` / `langchain-community` | Python, JS | LangChain | Multi-provider abstraction, chains, RAG |
| `llama-index` | Python | LlamaIndex | Data framework, RAG pipelines |

---

## 4. Agentic Frameworks

Frameworks for building AI agents — systems that use tools, make decisions, and complete multi-step tasks autonomously.

### First-Party / Platform-Level

| Framework | Company | Language | Key Concepts | Best For |
|---|---|---|---|---|
| [OpenAI Agents SDK](https://openai.github.io/openai-agents-python) | OpenAI | Python | Agents, handoffs, guardrails, tracing | Building structured multi-agent pipelines with OpenAI models |
| [Claude Code](https://claude.ai/code) | Anthropic | CLI / Python SDK | Agentic coding, tool use, subagents, MCP | Developer agents that read/write/fix code in real projects |
| [Google ADK](https://google.github.io/adk-docs) | Google | Python | Multi-agent, tool-use, Vertex integration | Google-native agent development |
| [Vertex AI Agent Builder](https://cloud.google.com/products/agent-builder) | Google | No-code + API | RAG-grounded agents, conversation flows | Enterprise chatbots and copilots on GCP |
| [Bedrock AgentCore](https://aws.amazon.com/bedrock/agents) | Amazon | Managed + SDK | Managed agents, Knowledge Bases, memory | AWS-native agents with managed infrastructure |
| [Llama Stack](https://github.com/meta-llama/llama-stack) | Meta | Python | Standardized API for Llama-based agent apps | Portable, open-source agent apps using Llama |
| [AutoGen](https://microsoft.github.io/autogen) | Microsoft | Python | Multi-agent conversation, group chat, nested agents | Complex multi-agent coordination and debate |
| [Semantic Kernel](https://learn.microsoft.com/semantic-kernel) | Microsoft | Python, C#, Java | Plugins, planners, memory, process framework | Enterprise AI orchestration in .NET/Python |

### Third-Party / Community

| Framework | Company | Language | Key Concepts | Best For |
|---|---|---|---|---|
| [LangGraph](https://langchain-ai.github.io/langgraph) | LangChain | Python, JS | Graph-based workflows, stateful agents, human-in-the-loop | Production-grade stateful agents |
| [LangChain](https://langchain.com) | LangChain | Python, JS | Chains, RAG, tools, memory, multi-provider | General GenAI app development |
| [LlamaIndex](https://llamaindex.ai) | LlamaIndex | Python, TS | Data ingestion, RAG, agent workflows | Data-heavy RAG applications |
| [CrewAI](https://crewai.com) | CrewAI | Python | Role-based agents, crews, tasks, hierarchical | Role-playing agent teams for business workflows |
| [Pydantic AI](https://ai.pydantic.dev) | Pydantic | Python | Type-safe agents, structured output | Strongly-typed, production-safe agents |
| [Haystack](https://haystack.deepset.ai) | deepset | Python | Pipelines, RAG, document processing | RAG pipelines and document search |
| [DSPy](https://dspy.ai) | Stanford NLP | Python | Programmatic prompt optimization | Optimizing prompts and pipelines automatically |

### Model Context Protocol (MCP)

| Tool | Description |
|---|---|
| [MCP (Model Context Protocol)](https://modelcontextprotocol.io) | Open standard by Anthropic — lets AI agents connect to tools, databases, files, APIs via a standard interface. Supported by Claude, Cursor, Windsurf, VS Code, and growing. |

---

## 5. IDE & Developer Coding Tools

Tools that help developers write, review, and fix code using AI.

### AI-Powered IDEs (Full IDE replacement)

| Tool | Company | Underlying Models | Key Features | Best For |
|---|---|---|---|---|
| [Cursor](https://cursor.sh) | Anysphere *(not Anthropic)* | Claude, GPT-4o | Inline chat, multi-file edits, codebase indexing, MCP | Developers wanting a fully AI-native IDE (VS Code-based) |
| [Windsurf](https://codeium.com/windsurf) | Codeium | Claude, GPT-4o | Cascade (multi-file agent), fast autocomplete | Similar to Cursor; strong autocomplete |
| [Kiro](https://kiro.dev) | Amazon (AWS) | Claude on Bedrock | Spec-driven development, hooks, agents | AWS-integrated AI IDE |
| [Zed](https://zed.dev) | Zed Industries | Claude, GPT-4o, local | Ultra-fast editor, collaborative, agentic panel | Performance-focused developers |

### AI Coding Extensions / Copilots (Plugin into existing editors)

| Tool | Company | IDE Support | Models | Best For |
|---|---|---|---|---|
| [GitHub Copilot](https://github.com/features/copilot) | Microsoft/GitHub | VS Code, JetBrains, Vim, Xcode | GPT-4o, Claude, Gemini | Most widely used; autocomplete + chat in any IDE |
| [Amazon Q Developer](https://aws.amazon.com/q/developer) | Amazon | VS Code, JetBrains, CLI | Amazon Nova + CodeWhisperer | AWS developers; security scanning, code reviews |
| [Gemini Code Assist](https://cloud.google.com/gemini/docs/codeassist) | Google | VS Code, JetBrains | Gemini 2.5 Pro | GCP developers; code completion + chat |
| [Tabnine](https://tabnine.com) | Tabnine | VS Code, JetBrains, Vim | Private fine-tuned models | Privacy-first; can run on-prem |
| [Codeium](https://codeium.com) | Codeium | VS Code, JetBrains, 40+ | Proprietary | Free autocomplete with broad IDE support |

### CLI / Terminal AI Tools

| Tool | Company | What It Does |
|---|---|---|
| [Claude Code](https://claude.ai/code) | Anthropic | CLI agent that reads, writes, and fixes code across an entire codebase; supports MCP, subagents, slash commands |
| [OpenAI Codex CLI](https://github.com/openai/codex) | OpenAI | Terminal-based coding agent using o-series models |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Google | Terminal agent using Gemini 2.5 Pro; 1M context |
| [Amazon Q CLI](https://aws.amazon.com/q/developer/) | Amazon | Terminal agent; translates natural language to shell commands |
| [Aider](https://aider.chat) | Aider | Open-source CLI pair programmer; works with any model |

---

## 6. ML / Data Science Platforms

Platforms for the full machine learning lifecycle: data prep, training, tuning, deployment, monitoring.

| Platform | Company | Key Capabilities | Best For |
|---|---|---|---|
| [Vertex AI](https://cloud.google.com/vertex-ai) | Google | Model training, MLOps, Feature Store, AutoML, RAG Engine, Model Garden | Full ML lifecycle on GCP |
| [Azure Machine Learning](https://azure.microsoft.com/products/machine-learning) / [AI Foundry](https://ai.azure.com) | Microsoft | Training, AutoML, prompt flow, model catalog, responsible AI | Enterprise ML on Azure |
| [Amazon SageMaker](https://aws.amazon.com/sagemaker) | Amazon | Training, tuning, deployment, pipelines, Canvas (no-code), JumpStart | End-to-end ML on AWS |
| [Databricks](https://databricks.com) | Databricks | Unified data + AI platform, MLflow, Delta Lake, Mosaic AI | Data-first ML; lakehouse architecture |
| [Hugging Face](https://huggingface.co) | Hugging Face | Model hub, datasets, Spaces (hosted apps), AutoTrain, Inference Endpoints | Open-source ML; largest model/dataset hub |
| [Weights & Biases](https://wandb.ai) | W&B | Experiment tracking, model registry, sweeps, evaluation | ML experiment management |
| [MLflow](https://mlflow.org) | Databricks (open source) | Tracking, packaging, deployment of ML models | Open-source ML tracking |
| [Modal](https://modal.com) | Modal Labs | Serverless GPU compute, easy model deployment | Fast GPU workloads without infra overhead |
| [Replicate](https://replicate.com) | Replicate | Run and fine-tune open models via API | Open-model API access with pay-per-use |

### Training Infrastructure / Hardware

| Resource | Provider | Purpose |
|---|---|---|
| Cloud TPU v5 / Trillium | Google Cloud | Google's custom AI accelerator chips; best for Gemini-scale training |
| Azure NDv5 (H100/GB200) | Microsoft | NVIDIA GPU clusters for large-scale training on Azure |
| AWS Trainium2 / Inferentia | Amazon | Amazon's custom chips; cost-efficient for training and inference |
| NVIDIA H100 / H200 / GB200 | NVIDIA (all clouds) | Industry-standard GPU for LLM training and serving |

---

## 7. Enterprise & Business Tools

AI products that augment existing enterprise workflows.

| Product | Company | Integrates With | Key Use Case |
|---|---|---|---|
| [Microsoft 365 Copilot](https://microsoft.com/microsoft-365/copilot) | Microsoft | Word, Excel, PowerPoint, Teams, Outlook | AI assistant across the entire M365 suite |
| [Copilot Studio](https://copilotstudio.microsoft.com) | Microsoft | Power Platform, M365, custom APIs | Build custom copilots for business without code |
| [Security Copilot](https://microsoft.com/security/copilot) | Microsoft | Microsoft Sentinel, Defender | AI for threat hunting, incident response |
| [ChatGPT Enterprise](https://openai.com/chatgpt/enterprise) | OpenAI | API + SSO + admin controls | Org-wide ChatGPT with data privacy guarantees |
| [Claude for Enterprise](https://anthropic.com/enterprise) | Anthropic | API + SSO + Projects | Long-context, policy-compliant Claude deployment |
| [Gemini for Google Workspace](https://workspace.google.com/intl/en/ai) | Google | Docs, Sheets, Gmail, Slides, Meet | AI features across the Google Workspace suite |
| [Amazon Q Business](https://aws.amazon.com/q/business) | Amazon | S3, SharePoint, Salesforce, Confluence | Enterprise Q&A over internal knowledge bases |
| [Salesforce Einstein](https://salesforce.com/artificial-intelligence) | Salesforce | CRM, Service Cloud, Marketing | AI within Salesforce products |
| [ServiceNow AI Agents](https://servicenow.com/ai) | ServiceNow | ITSM, HR, Finance workflows | Agentic AI for enterprise IT and operations |

---

## 8. Company-by-Company Summary

| Company | Chat / Consumer | Models | GenAI Dev Platform | Agentic Framework | IDE / Coding Tools | ML Platform |
|---|---|---|---|---|---|---|
| **OpenAI** | ChatGPT, SearchGPT, Operator | GPT-4o, o3, o4-mini, GPT-5 | OpenAI API, Realtime API, Assistants API | OpenAI Agents SDK | Codex CLI, GitHub Copilot (partner) | — |
| **Anthropic** | Claude.ai, Claude Voice | Claude 4 Opus/Sonnet/Haiku | Claude API, MCP | Claude Code (CLI Agent) | Claude Code CLI | — |
| **Google** | Gemini, Gemini Live, NotebookLM | Gemini 2.5 Pro/Flash, Gemma 3 | AI Studio, Vertex AI | Google ADK, Vertex Agent Builder | Gemini Code Assist, Gemini CLI | Vertex AI |
| **Microsoft** | Microsoft Copilot | Phi-4, MAI models | Azure AI Foundry, Azure OpenAI | AutoGen, Semantic Kernel | GitHub Copilot | Azure ML / AI Foundry |
| **Amazon** | Alexa+, Rufus | Nova, Titan | Amazon Bedrock | Bedrock AgentCore | Amazon Q Developer, Kiro IDE | SageMaker |
| **Meta** | Meta AI | Llama 4, Code Llama | Meta AI Studio | Llama Stack | — | PyTorch |
| **xAI** | Grok | Grok 3, Grok 3 Mini | Grok API | — | — | — |
| **Apple** | Apple Intelligence, Siri | Apple Foundation Models | Foundation Models Framework, Core ML | — | Xcode AI features | Core ML |
| **Mistral AI** | Le Chat | Mistral Large 2, Mistral Small 3 | Mistral API, La Plateforme | — | — | — |

---

## 9. Quick Reference — Choosing the Right Tool

### "I want to chat / get help with tasks"
→ **ChatGPT** (most features), **Claude.ai** (long docs, coding), **Gemini** (Google integration), **Perplexity** (research with sources)

### "I want to build a GenAI app using APIs"
→ Start with **OpenAI API** or **Anthropic API** for simplicity. Use **Vertex AI** or **Azure AI Foundry** for enterprise/multi-model.

### "I want to build AI agents"
→ **LangGraph** (production, stateful), **CrewAI** (role-based teams), **OpenAI Agents SDK** (OpenAI-native), **AutoGen** (multi-agent), **Google ADK** (GCP-native), **Claude Code** (agentic coding)

### "I want an AI coding assistant"
→ **GitHub Copilot** (widest IDE support), **Cursor** (AI-native IDE), **Claude Code** (CLI agent for whole codebase), **Amazon Q Developer** (AWS users)

### "I want to train or fine-tune my own models"
→ **AWS SageMaker**, **Google Vertex AI**, **Azure ML**, **Hugging Face AutoTrain**, **Databricks Mosaic AI**

### "I want to run open-source models locally"
→ **Ollama** (easiest local setup), **LM Studio**, **Hugging Face Transformers**, **vLLM** (self-hosted serving)

### "I want fast / cheap inference for open models"
→ **Groq** (fastest), **Together AI**, **Replicate**, **Hugging Face Inference**
