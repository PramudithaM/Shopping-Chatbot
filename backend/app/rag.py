from langchain.agents import create_agent  # builds an agent (LLM + tools)
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # message types
from langchain_core.tools import tool  # turns a function into a tool the LLM can call
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini chat model
from langchain_openai import ChatOpenAI  # OpenAI chat model

from app.config import GEMINI_API_KEY, GEMINI_MODEL, LLM_PROVIDER, OPENAI_MODEL  # settings from config.py
from app.vectorstores import get_store  # ChromaDB collections

TOP_K = 4  # how many chunks to retrieve for each search
MAX_HISTORY = 6  # how many previous messages we send to the model

SYSTEM_PROMPT = """You are ShopAssist, a customer support assistant for an online shop.

Rules:
- For every shop-related question, call a tool first. Use search_support for orders,
  delivery, returns, refunds, payments and policies. Use search_reviews for product
  quality, fit and what customers say.
- Answer ONLY using what the tools return. Never invent policies, prices, or facts.
- If the tool results do not contain the answer, say you are not sure and suggest
  contacting the support team.
- Keep answers short and friendly. Reply in the same language the customer writes in.
"""  # instructions for the model (this is the prompt)


def _search(collection: str, query: str):  # shared search used by both tools
    docs = get_store(collection).similarity_search(query, k=TOP_K)  # find the closest chunks
    if not docs:  # nothing found
        return "No relevant results found.", []

    content = "\n\n".join(f"[{i + 1}] {d.page_content}" for i, d in enumerate(docs))  # text for the model
    artifact = [{"collection": collection, "snippet": d.page_content[:200]} for d in docs]  # sources for the UI
    return content, artifact


@tool(response_format="content_and_artifact")  # content -> model, artifact -> our API
def search_support(query: str):
    """Search past customer support conversations. Use for questions about
    orders, delivery, returns, refunds, payments, accounts and store policies."""  # the model reads this to pick the tool
    return _search("support", query)


@tool(response_format="content_and_artifact")
def search_reviews(query: str):
    """Search customer product reviews. Use for questions about product quality,
    fit, comfort, what customers like or dislike, or to help choose products."""
    return _search("reviews", query)


def make_llm(provider: str | None = None):  # choose the LLM (provider from the UI, or LLM_PROVIDER from .env)
    provider = (provider or LLM_PROVIDER).lower()  # "gemini" or "openai"
    if provider == "gemini":  # Google Gemini
        return ChatGoogleGenerativeAI(model=GEMINI_MODEL, api_key=GEMINI_API_KEY, temperature=0, max_retries=4, timeout=60)  # retry a few times when Google is busy
    if provider == "openai":  # OpenAI
        return ChatOpenAI(model=OPENAI_MODEL, temperature=0)  # temperature 0 = stable answers
    raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'gemini'.")  # typo


def build_agent(provider: str | None = None, llm=None):  # create an agent for one provider
    llm = llm or make_llm(provider)  # use the chosen LLM
    return create_agent(llm, [search_support, search_reviews], system_prompt=SYSTEM_PROMPT)


async def answer(agent, message: str, history: list[dict]) -> tuple[str, list[dict]]:
    messages = history[-MAX_HISTORY:] + [{"role": "user", "content": message}]  # recent history + new question
    result = await agent.ainvoke({"messages": messages})  # run the agent (async)
    out = result["messages"]  # all messages, including tool calls

    last_human = max(i for i, m in enumerate(out) if isinstance(m, HumanMessage))  # position of our question
    sources: list[dict] = []
    for m in out[last_human + 1 :]:  # only messages created for this question
        if isinstance(m, ToolMessage) and isinstance(m.artifact, list):  # tool results carry the sources
            sources.extend(m.artifact)

    final = next(m for m in reversed(out) if isinstance(m, AIMessage))  # the last AI message = the answer
    return final.text, sources