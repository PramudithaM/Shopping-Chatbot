# ShopAssist AI

An AI customer support chatbot for an online shop. It answers questions from real data using **retrieval-augmented generation (RAG)**, and an LLM agent decides which data source to search for each question.

Built with FastAPI, React, LangChain, Hugging Face embeddings and ChromaDB. The LLM can be switched in the UI between Gemini, OpenAI and Groq.

<img width="1274" height="1030" alt="Screenshot 2026-10-03 174249" src="https://github.com/user-attachments/assets/38385fe5-abf6-4e66-8c09-2014e2b38b4d" />

## Features

- **Support answers** from past customer support conversations (returns, delivery, cancellations, account issues).
- **Product opinions** from customer reviews (comfort, fit, quality).
- **Product ranking** by price and rating (cheapest, best rated, under a budget) through a dedicated tool.
- **Sources** shown under every answer, so you can see which data it came from.
- **Conversation history**, so follow-up questions work.
- **LLM selector** in the chat header (only providers that have an API key are shown).
- **Hallucination guard**: the system prompt tells the model to answer only from tool results and to say it is not sure otherwise.
- **Async FastAPI backend** that handles concurrent requests.

## How it works

```
 Hugging Face datasets
   │  load, clean, chunk (LangChain text splitter)
   ▼
 Embeddings (sentence-transformers/all-MiniLM-L6-v2)
   ▼
 ChromaDB  ── collection "support"
           └─ collection "reviews"          products.json (sample prices)
                      ▲                              ▲
                      │ search_support               │ search_products
                      │ search_reviews               │
 React chat UI ──► FastAPI /chat ──► LangChain agent (Gemini / OpenAI / Groq)
```

The agent reads the question, picks one or more tools, reads what they return, and writes the answer. Each tool also returns its source snippets, which the UI shows.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| RAG | LangChain, ChromaDB, Hugging Face `sentence-transformers` |
| LLMs | Google Gemini, OpenAI, Groq (selectable) |
| Frontend | React, Vite, Tailwind CSS |
| Data | Hugging Face `datasets` |

## Datasets

- [`NebulaByte/E-Commerce_Customer_Support_Conversations`](https://huggingface.co/datasets/NebulaByte/E-Commerce_Customer_Support_Conversations): support conversations (1,000 rows).
- [`Censius-AI/ECommerce-Women-Clothing-Reviews`](https://huggingface.co/datasets/Censius-AI/ECommerce-Women-Clothing-Reviews): clothing reviews (23,486 rows, the first 5,000 are embedded by default).

Check the license on each dataset page before reusing them.

## Setup

You need Python 3.11 or newer, Node.js 20.19 or newer, and an API key for at least one LLM provider.

### 1. Backend

```bash
cd backend
python -m venv venv            # or use conda
# Windows: venv\Scripts\activate      Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env` from the example and add your key(s):

```bash
cp .env.example .env
```

```dotenv
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-3.8-flash

OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4.1-mini

# optional, free tier
GROQ_API_KEY=your-groq-key
GROQ_MODEL=openai/gpt-oss-20b
```

Model names change over time. Use a model that is available on your account and supports tool calling.

### 2. Build the data (once)

```bash
python scripts/01_explore.py            # download and inspect the datasets
python scripts/02_prepare_chunks.py     # clean and chunk the text
python scripts/03_build_vectorstore.py  # embed the chunks into ChromaDB
python scripts/04_build_products.py     # build products.json (sample prices)
python scripts/check_llm.py             # optional: check that your LLM key works
```

### 3. Run the backend

```bash
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend calls `http://localhost:8000` by default (set `VITE_API_URL` to change it).

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Server status |
| GET | `/providers` | LLMs that have a key configured, and the default |
| POST | `/chat` | `{ "message": "...", "history": [], "provider": "gemini" }` returns `{ "answer": "...", "sources": [...] }` |

## Example questions

- `Can I return a product after 20 days?` (support data)
- `Which dresses do customers say are comfortable?` (reviews)
- `Suggest the cheapest dress that customers rate highly.` (products)
- `Do you accept Bitcoin?` (not in the data, so the bot should say it is not sure)

## Project structure

```
backend/
├── app/
│   ├── config.py          settings and .env loading
│   ├── vectorstores.py    embeddings and ChromaDB collections
│   ├── rag.py             tools, LLM selection, agent
│   └── main.py            FastAPI app
├── scripts/               one-time data pipeline (01 to 04) and key check
├── requirements.txt
└── .env.example
frontend/
└── src/
    ├── api.js             calls to the backend
    └── components/        Chat.jsx, Message.jsx
```

## Limitations

- **Prices are synthetic.** The reviews dataset has no prices, so `04_build_products.py` generates sample prices per clothing class. The bot says "sample price" when it mentions one. Replace `data/products.json` with real product data to use it for a real shop.
- Product names are generated (`Dresses #1080`) because the dataset has no product titles.
- The data comes from two unrelated public datasets (an electronics and appliances support dataset, and a women's clothing review dataset), so it is a demo, not a real shop.
- Embeddings are English-focused (`all-MiniLM-L6-v2`).
- Free LLM tiers have rate limits and can return busy or rate-limit errors.

## Ideas for next steps

- Streaming responses
- Docker and deployment
- Rate limiting and authentication
- Multilingual embeddings
- Real product catalog and price filters in the UI
