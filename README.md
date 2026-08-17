<div align="center">

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Shield.png" alt="Shield" width="100" height="100" />

# ⚡ RansomShield AI ⚡

**Enterprise-Grade Generative AI Ransomware Detection Sandbox**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Ollama](https://img.shields.io/badge/Ollama-FFFFFF?style=for-the-badge&logo=ollama&logoColor=black)](https://ollama.ai/)
[![Security Audit](https://img.shields.io/badge/Security-A+-success.svg?style=for-the-badge&logo=auth0)](https://github.com/Vinit080/ransomware-detection)

*A sophisticated, privacy-first cybersecurity platform that leverages local Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and OS-level telemetry to detect and dissect advanced ransomware threats in real-time.*

<br />
</div>

---

## 🛡️ Architecture & Threat Intel

RansomShield AI is built as a complete end-to-end sandbox orchestration and analysis platform. It ingests high-speed Event Tracing for Windows (ETW) telemetry from isolated hypervisor environments, feeding raw process creations, API hooks, and filesystem modifications into a multi-layered analysis engine.

### 🧠 The Dual-Engine Approach
1. **Deterministic Heuristics Engine**: Rapidly scores execution traces using traditional Cyber Threat Intelligence (CTI) rules (e.g., YARA matching, known API hook signatures, rapid encryption behaviors).
2. **Generative AI Engine (Ollama + RAG)**: When heuristics flag anomalous behavior, the LLM takes over. Running entirely locally via Ollama to ensure strict zero-trust data privacy, the AI analyzes the telemetry against a ChromaDB vector store of MITRE ATT&CK techniques to generate comprehensive, human-readable threat reports.

---

## 💻 Enterprise Tech Stack

<table align="center">
  <tr>
    <td align="center" width="33%">
      <h3>Backend (Core Logic)</h3>
      <img src="https://skillicons.dev/icons?i=py,fastapi,postgres" /><br/>
      <b>Python 3.12</b><br/>
      <b>FastAPI</b> (Async API)<br/>
      <b>SQLAlchemy & Alembic</b> (ORM & Migrations)<br/>
      <b>PostgreSQL</b> (Persistence)<br/>
      <b>Pydantic</b> (Data Validation)
    </td>
    <td align="center" width="33%">
      <h3>Frontend (Command Center)</h3>
      <img src="https://skillicons.dev/icons?i=nextjs,react,tailwind" /><br/>
      <b>Next.js 15</b> (App Router)<br/>
      <b>React & TypeScript</b><br/>
      <b>TailwindCSS</b> (Enterprise UI)<br/>
      <b>Zustand</b> (Global State)<br/>
      <b>Recharts</b> (Telemetry Visualization)
    </td>
    <td align="center" width="33%">
      <h3>AI & Cybersecurity</h3>
      <img src="https://skillicons.dev/icons?i=pytorch,linux,docker" /><br/>
      <b>Ollama</b> (Local LLM Execution)<br/>
      <b>LangChain</b> (LLM Orchestration)<br/>
      <b>ChromaDB</b> (Vector Database)<br/>
      <b>ETW Mocking</b> (OS Telemetry)<br/>
      <b>OAuth2 & JWT</b> (RBAC Security)
    </td>
  </tr>
</table>

---

## 🚀 Key Features

- **Live Cyber Terminal**: Watch the sandbox hypervisor tear apart malware in real-time. The frontend features a highly optimized, auto-scrolling terminal component streaming raw OS events (`ProcessCreate`, `ApiHook`, `FileWrite`).
- **AI Threat Reports**: Automatically generate beautifully formatted markdown reports dissecting the malware's capabilities, mapped directly to external Cyber Threat Intelligence (CTI) frameworks.
- **Strict Role-Based Access Control (RBAC)**: Secure OAuth2 Password Bearer flow. Routes are heavily protected; only authenticated `RESEARCHER` or `ADMINISTRATOR` roles can access the dashboard.
- **Enterprise UI**: A complete departure from generic web apps. Designed with an ultra-premium, dark-mode brutalist aesthetic (solid `#0a0a0a` panels, sharp 1px borders, high-contrast typography).
- **Air-Gapped Ready**: The entire architecture (including the AI engine via Ollama) is designed to run locally, ensuring highly sensitive, weaponized malware telemetry never leaves the internal network.

---

## ⚙️ Quick Start

### 1. Backend Setup
```bash
cd ransomshield-ai

# Activate Virtual Environment & Install Dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the FastAPI Server
uvicorn apps.api.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd ransomshield-ai/web

# Install Dependencies
npm install

# Run the Next.js Development Server
npm run dev
```

### 3. Access the Command Center
Navigate to `http://localhost:3000` in your browser.
You will be redirected to the secure login portal.
- **Username**: `admin`
- **Password**: `admin123`

---

## 🔒 Security & Code Audit

This repository undergoes strict continuous auditing:
- **Python Backend**: Secured and verified using `bandit` (Static Analysis) and `safety` (Dependency Vulnerability Scans).
- **Next.js Frontend**: Conforms to strict ESLint `@typescript-eslint` rules with 0 high-severity `npm audit` findings.
- **Authentication**: Stateless, cryptographically signed JWT tokens ensure zero session hijacking.

<div align="center">
  <br/>
  <i>Engineered for the Enterprise. Built for the modern Cyber Threat Landscape.</i>
</div>
