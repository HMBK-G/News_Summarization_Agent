import requests
import google.generativeai as genai
from google.adk.agents import Agent

genai.configure(api_key="Your_API_KeY*********")
model = genai.GenerativeModel("gemini-1.5-flash")

#  Summarization function
def summarize_news(text: str) -> str:
    try:
        prompt = (
            "Summarize the following news content into 10–12 concise, non-repetitive bullet points. "
            "Only include information directly related to the topic. Avoid speculation or unrelated global issues.\n\n"
            f"{text}"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Summarization failed: {str(e)}"

#  Grammar correction function
def correct_grammar(text: str) -> str:
    try:
        prompt = f"Correct any grammatical or punctuation errors in the following summary. Keep the bullet point format:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Grammar correction failed: {str(e)}"

#  News fetching function (without displaying URLs)
def fetch_news(query: str, region: str = "global") -> dict:
    API_KEY = "CSE_API_KEY_******"
    CX = "*********"

    try:
        search_query = f"{query} latest news"
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": search_query,
            "hl": "en"
        }

        if region.lower() != "global":
            params["gl"] = region.lower()

        response = requests.get(url, params=params)
        data = response.json()

        if "items" not in data or not data["items"]:
            return {"status": "error", "error_message": "No news found."}

        contents = []
        for item in data["items"][:10]:
            title = item.get("title", "").strip()
            snippet = item.get("snippet", "").strip()
            contents.append(f"{title}\n{snippet}")

        combined = "\n\n".join(contents)
        return {"status": "success", "report": combined[:12000]}

    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# Combined summarization + grammar correction agent
def summarize_news_from_query(query: str, region: str = "global") -> dict:
    news_result = fetch_news(query, region)
    if news_result["status"] != "success":
        return news_result

    summary = summarize_news(news_result["report"])
    cleaned_summary = correct_grammar(summary)
    return {
        "status": "success",
        "report": cleaned_summary
    }

# Register agent with ADK
root_agent = Agent(
    name="news_summary_agent",
    model="gemini-2.0-flash",
    description="Fetches top news using Google and summarizes it using Gemini.",
    instruction="You are an assistant that finds the latest news and summarizes it clearly, then corrects grammar.",
    tools=[summarize_news_from_query]
)

#  Test CLI
if __name__ == "__main__":
    query = input("Enter your news query: ")
    result = summarize_news_from_query(query)
    print(result.get("report", result.get("error_message", "No output.")))