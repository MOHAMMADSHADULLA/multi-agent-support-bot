# 🤖 Multi-Agent AI Support Bot

A production-style multi-agent customer support chatbot built for a travel-booking platform, **TravelZone**.

The system uses four specialized agents to route customer requests, retrieve relevant knowledge, generate grounded responses, and handle requests that require escalation or tool usage.

---

## 🌐 Live Demo

🚀 **Live Application:**  
https://multi-agent-support-bot.onrender.com/

> The application is deployed on Render's free tier and may sleep after inactivity. The first request after inactivity may take some time to start.

---

## ✨ Features

- 🤖 Multi-agent AI architecture
- 🎯 Intelligent request orchestration
- 🔎 Retrieval-Augmented Generation (RAG)
- 📚 Markdown-based knowledge base
- 🧠 TF-IDF + cosine similarity retrieval
- 💬 Context-grounded AI responses
- 🛠️ Tool/function calling
- 📦 Mock order-status lookup
- 🎫 Mock support-ticket creation
- 🔄 OpenAI / Google Gemini / Mock LLM providers
- ⚡ FastAPI backend
- 🌐 Lightweight web interface
- 🧪 Automated Pytest test suite
- 🐳 Docker support
- 🔁 GitHub Actions CI
- ☁️ Render deployment

---

# 🏗️ Architecture

```mermaid
flowchart TD

    A[👤 User Message] --> B[🎯 Orchestrator Agent]

    B --> C[🔎 Retrieval Agent]

    C -->|Confident Match| D[💬 Support Agent]

    D --> E[✅ Response]

    C -->|No Confident Match| F[🚨 Escalation Agent]

    F -->|Order Request| G[📦 check_order_status]

    F -->|Unsupported Issue| H[🎫 create_support_ticket]

    G --> E
    H --> E


🤖 Multi-Agent System

The application separates responsibilities across four agents.

1. 🎯 Orchestrator Agent

Coordinates the overall request flow.

Receives the user's message
Determines the appropriate workflow
Routes requests to the retrieval system
Connects retrieval, support, and escalation workflows
2. 🔎 Retrieval Agent

Searches the knowledge base for relevant information.

Technology:

TF-IDF vectorization
Cosine similarity
Markdown knowledge base
Confidence scoring

If a relevant match is found, the request is passed to the Support Agent.

If no confident match is found, the request is passed to the Escalation Agent.

3. 💬 Support Agent

Generates responses using the user's question and retrieved knowledge-base context.

This helps keep responses grounded in available documentation.

4. 🚨 Escalation Agent

Handles requests that cannot be confidently answered using the knowledge base.

It can use tools such as:

check_order_status
create_support_ticket    

🧠 RAG Pipeline

The project uses a lightweight retrieval-augmented generation pipeline.
Knowledge Base
      ↓
Document Loading
      ↓
TF-IDF Vectorization
      ↓
User Query
      ↓
Cosine Similarity
      ↓
Relevant Context
      ↓
Support Agent
      ↓
Grounded Response

Why TF-IDF?

TF-IDF was selected for this project because it provides:

Lightweight retrieval
Fast startup
No external embedding API
No vector database requirement
Deterministic results
Easy testing
Simple deployment

The retrieval layer can later be upgraded to embedding-based search using technologies such as Chroma or pgvector.
🛠️ Tool Calling

The Escalation Agent can invoke application tools based on the user's request.

check_order_status

Used for order-related requests.

Example:
User:
Check the status of order A1001.

↓
Escalation Agent
↓
check_order_status()
↓
Order Information
↓
Response
create_support_ticket

Used when an issue requires escalation.

Example:
User:
I have an issue that isn't covered in the knowledge base.

↓
Escalation Agent
↓
create_support_ticket()
↓
Ticket Information
↓
Response
The current order lookup and ticket system use mock/in-memory implementations for demonstration and testing. They are not connected to real production systems.

💻 Tech Stack
| Category   | Technologies                        |
| ---------- | ----------------------------------- |
| Backend    | Python, FastAPI, Pydantic, Uvicorn  |
| AI / ML    | OpenAI, Google Gemini, scikit-learn |
| Retrieval  | TF-IDF, Cosine Similarity           |
| Frontend   | HTML, CSS, JavaScript               |
| Testing    | Pytest                              |
| DevOps     | Docker, GitHub Actions              |
| Deployment | Render                              |

📁 Project Structure
multi-agent-support-bot/
│
├── app/
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── retrieval_agent.py
│   │   ├── support_agent.py
│   │   └── escalation_agent.py
│   │
│   ├── data/
│   │   └── knowledge-base files
│   │
│   ├── static/
│   │   └── index.html
│   │
│   ├── rag.py
│   ├── tools.py
│   ├── llm_client.py
│   ├── config.py
│   └── main.py
│
├── tests/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md

💬 Example Requests
Knowledge Base Request
User:
How do I cancel my booking?

↓

Orchestrator
↓

Retrieval Agent
↓

Relevant knowledge found

↓

Support Agent
↓

Grounded response
Order Request
User:
Check order A1001.

↓

Orchestrator
↓

Retrieval Agent

↓

Escalation Agent

↓

check_order_status()

↓

Response
Unsupported Request
User:
I have an issue that isn't covered in the FAQ.

↓

Orchestrator
↓

Retrieval Agent

↓

No confident match

↓

Escalation Agent

↓

create_support_ticket()

↓

Response

🚀 Getting Started
1. Clone the Repository
git clone https://github.com/MOHAMMADSHADULLA/multi-agent-support-bot.git
cd multi-agent-support-bot

2. Create a Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate

Linux / macOS
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file using .env.example.

For local development without an API key:
LLM_PROVIDER=mock

For OpenAI:
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key

For Google Gemini:
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=your_model_name
Use a model name supported by your configured API/account.

5. Run the Application
uvicorn app.main:app --reload
Open:
http://localhost:8000

📚 API

FastAPI interactive documentation:
http://localhost:8000/docs

Health Check
GET /health

Chat
POST /chat
Example request:
{
  "message": "How do I cancel a booking?"
}

🐳 Docker
Build
docker build -t multi-agent-support-bot .
Run
docker run -p 8000:8000 -e LLM_PROVIDER=mock multi-agent-support-bot
Then open:

http://localhost:8000

🧪 Testing

Run the automated test suite:

pytest -v

Tests cover:

Retrieval relevance
Retrieval confidence scoring
Individual agent behavior
Agent orchestration
API behavior
Tool execution

The project currently contains 16 automated tests.

🔁 CI/CD

GitHub Actions automatically runs the test suite on repository changes.

Git Push
   ↓
GitHub Actions
   ↓
Install Dependencies
   ↓
Run Tests
   ↓
Validation
☁️ Deployment

The application is currently deployed using Render.

🚀 Live Demo:
https://multi-agent-support-bot.onrender.com/

The Dockerized application can also be deployed to platforms such as:

Railway
Fly.io
AWS ECS
AWS Fargate
AWS App Runner
⚠️ Current Limitations

This project is designed as a portfolio and demonstration application.

Current limitations:

Order lookup uses mock/in-memory data
Support tickets use mock/in-memory data
Retrieval uses TF-IDF instead of semantic embeddings
No persistent conversation database
No production helpdesk integration
No real order-management integration
No authentication system
Render free-tier deployment may sleep after inactivity
🚀 Future Improvements

Potential extensions include:

🔹 Embedding-based semantic search
🔹 Chroma or pgvector integration
🔹 PostgreSQL conversation storage
🔹 Persistent support tickets
🔹 Real order-management integration
🔹 Zendesk / Freshdesk integration
🔹 Streaming AI responses
🔹 User authentication and JWT
🔹 Role-based access control
🔹 Rate limiting
🔹 Agent tracing and observability
🔹 LLM usage monitoring
🎯 What This Project Demonstrates
Multi-agent AI architecture
Agent orchestration
Retrieval-Augmented Generation
Information retrieval
TF-IDF and cosine similarity
LLM integration
Tool/function calling
FastAPI API development
Modular software architecture
Automated testing
Docker containerization
GitHub Actions CI
Cloud deployment
🔗 Links

Live Demo:
https://multi-agent-support-bot.onrender.com/

GitHub Repository:
https://github.com/MOHAMMADSHADULLA/multi-agent-support-bot

📄 License

This project is intended for educational, portfolio, and demonstration purposes.


**This is the version I would use on your GitHub.** It is detailed enough to demonstrate the AI/engineering work, but avoids the repeated sections from the longer version.

