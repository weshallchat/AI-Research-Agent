# 🔬 AI Research Agent

An intelligent multi-agent system that conducts automated research on any topic, synthesizes findings from multiple sources, and generates comprehensive markdown reports with visualizations.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)

## ✨ Features

- **🔄 Query Transformation**: Converts vague queries into research-optimized questions
- **📋 Intelligent Planning**: Creates structured research plans with multiple angles
- **✅ Relevancy Checking**: Validates research plans before execution
- **🔍 Multi-Source Search**: Searches DuckDuckGo, Wikipedia, and more
- **📊 Evidence Extraction**: Extracts and scores relevant evidence from sources
- **📝 Report Synthesis**: Generates comprehensive markdown reports
- **📈 Visual Analytics**: Creates PNG charts for evidence distribution
- **🖥️ Gradio UI**: User-friendly web interface
- **🛡️ Fallback System**: LLM-generated answers when research isn't feasible

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Query                               │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Query Transformer                             │
│              (Lightweight LLM - gpt-4o-mini)                    │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Planning Agent                               │
│                  (Creates research plan)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Relevancy Checker                              │
│           (Validates plan against query)                        │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
        ✅ Relevant                    ❌ Not Relevant
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌─────────────────────────────────┐
│    Search Agent          │    │   Direct Answer Generator       │
│    (Web + Wikipedia)     │    │   (LLM-generated response)      │
└──────────┬───────────────┘    └─────────────────────────────────┘
           ▼
┌──────────────────────────┐
│   Evidence Extractor     │
│   (Score & extract)      │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│   Synthesis Agent        │
│   + Visual Generator     │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│   Markdown Report        │
│   + PNG Charts           │
└──────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API Key

### Installation

```bash
# Clone the repository
git clone https://github.com/weshallchat/AI-Research-Agent.git
cd AI-Research-Agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### Run the Application

**Option 1: Gradio Web UI (Recommended)**
```bash
python app.py
```
Then open the URL shown in the terminal (Ex: `https://2ede52a197d64e8c60.gradio.live`).
Markdown reports can be found in ./AI-Research-Agent/output folder.

**Option 2: Run Tests**
```bash
python tests/run_all_tests.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (for enhanced web search)
SERPER_API_KEY=your_serper_key
BING_API_KEY=your_bing_key
GOOGLE_API_KEY=your_google_key
GOOGLE_CX=your_google_cx
```

### Model Configuration

The system uses two LLM tiers:

| Task | Model | Purpose |
|------|-------|---------|
| Query Transformation | `gpt-4o-mini` | Fast, cost-effective |
| Relevancy Checking | `gpt-4o-mini` | Simple classification |
| Planning & Synthesis | `gpt-4o` | Complex reasoning |

Configure in `src/utils/helpers.py`.

## 📁 Project Structure

```
AI-Research-Agent/
├── app.py                    # Gradio web UI
├── requirements.txt          # Dependencies
├── .env                      # API keys (create this)
├── outputs/                  # Generated reports & charts
│   ├── research_report_*.md
│   ├── evidence_*.png
│   └── source_*.png
├── src/
│   ├── orchestrator.py       # Main coordinator
│   ├── agents/
│   │   ├── query_transformer.py   # Query optimization
│   │   ├── planner.py             # Research planning
│   │   ├── relevancy_checker.py   # Plan validation
│   │   ├── searcher.py            # Web search
│   │   ├── extractor.py           # Evidence extraction
│   │   ├── synthesizer.py         # Report generation
│   │   ├── visual_generator.py    # Chart creation
│   │   └── direct_answer_generator.py  # Fallback LLM answers
│   ├── tools/
│   │   ├── web_search.py          # Search providers
│   │   └── wikipedia_tool.py      # Wikipedia API
│   ├── prompts/
│   │   └── templates.py           # LLM prompt templates
│   └── utils/
│       └── helpers.py             # LLM setup utilities
└── tests/
    ├── run_all_tests.py           # Test runner
    ├── unit/                      # Unit tests
    ├── integration/               # Integration tests
    ├── e2e/                       # End-to-end tests
    └── edge_cases/                # Edge case tests
```

## 🔬 How It Works

### 1. Query Transformation
```
Input:  "AI in healthcare"
Output: "What are the applications, benefits, and challenges of 
         artificial intelligence in healthcare delivery and diagnosis?"
```

### 2. Research Planning
```json
{
  "research_angles": [
    "Clinical applications of AI",
    "Benefits for patient outcomes",
    "Challenges and limitations"
  ],
  "search_queries": [
    "AI healthcare clinical applications 2024",
    "machine learning medical diagnosis benefits"
  ],
  "focus_areas": ["accuracy", "bias", "adoption"]
}
```

### 3. Relevancy Check
- Validates that the plan actually addresses the query
- Score threshold: 0.6
- If below threshold → Fallback to LLM-generated answer

### 4. Evidence Extraction
- Searches multiple sources
- Extracts key claims, data, quotes
- Scores relevance (0.0 - 1.0)

### 5. Report Synthesis
- Markdown format with headers
- Executive summary
- Key findings by angle
- Visual charts (PNG)
- References section

## 📊 Output Example

Reports include:
- **Metadata**: Date, topic, source count
- **Executive Summary**: Overview of findings
- **Visual Analytics**: Evidence distribution charts
- **Key Findings**: Organized by research angle
- **References**: Linked sources

## 🧪 Testing

```bash
# Run all unit/integration tests (no API calls)
python tests/run_all_tests.py

# Run end-to-end tests (uses real API)
python tests/e2e/test_full_research.py

# Run edge case tests
python tests/edge_cases/test_edge_cases.py
```

### Test Coverage

| Test Type | Purpose | API Calls |
|-----------|---------|-----------|
| Unit | Individual components | ❌ Mocked |
| Integration | Component interactions | ❌ Mocked |
| E2E | Full pipeline | ✅ Real |
| Edge Cases | Boundary conditions | ✅ Real |

## 🛠️ Development

### Adding a New Agent

1. Create `src/agents/your_agent.py`
2. Add prompt template to `src/prompts/templates.py`
3. Import in `src/orchestrator.py`
4. Add to orchestration flow

### Adding a New Search Provider

1. Create provider class in `src/tools/web_search.py`
2. Implement `search()` method returning `SearchResult` objects
3. Add to `SearchAgent._create_tool_chain()`

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - LLM framework
- [OpenAI](https://openai.com/) - GPT models
- [Gradio](https://gradio.app/) - Web UI
- [DuckDuckGo](https://duckduckgo.com/) - Search API
