import streamlit as st
from openai import OpenAI
from tavily import TavilyClient
from concurrent.futures import ThreadPoolExecutor

# --- Hardcoded API Keys ---
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# --- Functions ---
def ask_ai(prompt, model="gpt-4"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def web_search(query):
    response = tavily.search(query=query, max_results=5, search_depth="basic")
    combined_content = ""
    for result in response.get("results", []):
        combined_content += result.get("content", "") + "\n\n"
    return combined_content or "No research content found."

def summarizer_agent(research):
    prompt = f"Summarize the following research into a short paragraph:\n{research}"
    return ask_ai(prompt)

def facebook_agent(summary):
    prompt = f"""
    You are a witty and creative facebook caption writer.

Based on the summary below, craft a short, catchy, and fun caption. Use emojis and 2–3 relevant hashtags where appropriate. Avoid sounding too formal.

Summary:
{summary}

Guidelines:
- Keep it under 150 characters if possible.
- Feel free to use humor or trending slang.
    """
    return "📘 Facebook Post:\n" + ask_ai(prompt)

def linkedin_agent(summary):
    prompt = f"""
You are a personal branding expert for LinkedIn.

Write a professional, insightful, and engaging LinkedIn post based on the summary below. The tone should be thoughtful and value-driven. Avoid hashtags unless contextually necessary.

User request:
{summary}

Guidelines:
- Write in the first person.
- Keep it within 2–4 short paragraphs.
- Aim to educate, inspire, or provoke thought.
    """
    return "💼 LinkedIn Post:\n" + ask_ai(prompt)

def twitter_agent(summary):
    prompt = f"""
You are a social media content expert.

Write a highly engaging and concise **Twitter/X post** based on the following summary:

\"\"\"{summary}\"\"\"

**Guidelines:**
- Use a catchy hook to grab attention in the first few words.
- Add 1–2 relevant emojis to enhance visual appeal.
- Include 2–3 relevant and trending hashtags at the end (e.g., #AI, #MarketingTips).
- Stay within Twitter's character limit (280 characters).
- Avoid technical jargon. Keep it easy to read and impactful.
- Ensure it aligns with Twitter’s fast-scrolling, attention-seeking style.

Respond only with the final tweet, no additional text.
"""
    return "🐦 Twitter Post:\n" + ask_ai(prompt)

def run_agents(topic):
    research = web_search(topic)
    summary = summarizer_agent(research)

    agent_functions = [facebook_agent, linkedin_agent, twitter_agent]

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda fn: fn(summary), agent_functions))

    return research, summary, results

# --- Streamlit UI ---
st.title("🤖 PostBot AI - Multi-Platform Post Generator")
st.markdown("Enter a topic and generate platform-specific posts with one click!")

topic = st.text_input("Enter a topic to generate social posts", value="Ind vs Pak war 2025")

if st.button("Generate Posts"):
    if topic.strip() == "":
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Thinking... 🧠"):
            research, summary, posts = run_agents(topic)

        st.subheader("🔍 Step 1: Web Research Output")
        st.code(research, language='markdown')

        st.subheader("🧠 Step 2: Summarized Research")
        st.info(summary)

        st.subheader("📱 Step 3: Generated Social Media Posts")

        st.markdown("### 📘 Facebook")
        st.success(posts[0])

        st.markdown("### 💼 LinkedIn")
        st.success(posts[1])

        st.markdown("### 🐦 Twitter")
        st.success(posts[2])
