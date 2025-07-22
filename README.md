# 🧠 GenAI Agents CLI Infrastructure

The **GenAI Agents CLI** project, developed as part of the **"Lead with AI Agents"** Hackathon!

This repository provides a complete infrastructure to run intelligent, modular agents through a CLI, built on top of the [GenAI AgentOS](https://github.com/genai-works-org/genai-agentos) stack.

---

## 🚀 Overview

## 🧠 Architecture Overview

Each agent performs a focused task and can work independently or together in a flow:

```bash
Speech (User) 
   ↓
Audio Agent (Speech → Text)
   ↓
Summarization Agent (Text → Summary)
   ↓
Translation Agent (Summary → Translated Text)
   ↓
Speech Agent (Text → Voice)
```

---

### ✅ Agents Implemented

| Agent Name          | Purpose                                                  |
| ------------------- | -------------------------------------------------------- |
| `audio_agent`       | Captures user speech and converts it to text             |
| `summary_agent`     | Summarizes long text using BART-based models             |
| `translation_agent` | Translates text between 20+ languages using mBART & Opus |
| `speech_agent`      | Converts text into speech                                |

---

## 🤖 Available Agents

### 1. **Audio Agent** (`audio_agent.py`)

* **Purpose**: Captures audio input and converts it to text using transcription models.
* **Usage**: Takes raw voice input, returns a transcribed string.

### 2. **Summarization Agent** (`summarization_agent.py`)

* **Purpose**: Summarizes long input text into concise summaries.
* **Model**: `facebook/bart-large-cnn`
* **Features**:

  * Intelligent chunking for large documents.
  * Language detection (supports English, French, Arabic, German).

### 3. **Translation Agent** (`translation_agent.py`)

* **Purpose**: Translates text from one language to another.
* **Model**: `facebook/mbart-large-50-many-to-many-mmt`
* **Capabilities**:

  * Auto language detection.
  * Smart chunking for long/complex scripts.
  * Fallback to `Helsinki-NLP/opus-mt-mul-en` if needed.

### 4. **Speech Agent** (`speech_agent.py`)

* **Purpose**: Converts any text into spoken language.
* **Tool**: `gTTS` (Google Text-to-Speech)
* **Features**:

  * Multi-language support with language fallback mapping.
  * Auto-plays or returns audio file for playback.

---

| Agent               | Supported Languages |
| ------------------- | ------------------- |
| Audio Agent         | ✅ English           |
| Summarization Agent | ✅ English           |
| Translation Agent   | ✅ 20+ languages     |
| Speech Agent        | ✅ 20+ languages     |

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/genai-works-org/genai-agentos
cd genai-agentos
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` File

Create a `.env` file in the root directory:

```env
AGENT_JWT=your_token_here
```

> Replace `your_token_here` with your actual JWT token.

---

## 🚀 Running CLI Agents

Each agent can be invoked using the `cli.py` interface. For example:

```bash
python cli.py summary_agent "Your long text to summarize here"

python cli.py translation_agent "Hello, world!" en fr

python cli.py speech_agent "Bonjour tout le monde"

python cli.py audio_agent
```

---

## 🧪 Example Workflow

1. Speak into the mic (Audio Agent)
2. Transcription goes to Summarization Agent
3. Summary gets translated to another language via Translation Agent
4. Final result is spoken back via the Speech Agent

---

## 📌 Tech Stack

* **Transformers (HuggingFace)**
* **GenAI AgentOS SDK**
* **Google Text-to-Speech (gTTS)**
* **Streamlit (optional for GUI)**
* **gTTS, LangDetect, MBart, BART**

---

## 🎯 Use Cases

* 🔁 Real-time multilingual translation with voice output
* 📰 Summarizing long content into digestible audio in another language
* 🧑‍🏫 Assistive tech for reading-impaired or visually impaired users
* 🗣️ Voice-based note-taking or journaling with summaries
* 🌐 Language learning companion tool

---

## 🙌 Acknowledgements

* Built on top of [GenAI AgentOS](https://github.com/genai-works-org/genai-agentos)
* Uses powerful models from [HuggingFace Transformers](https://huggingface.co/models)

---

> ⚡️ Designed for the "Lead with AI Agents" hackathon.
