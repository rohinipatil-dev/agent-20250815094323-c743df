import streamlit as st
from openai import OpenAI

# ---------------------------
# Configuration and Utilities
# ---------------------------

def build_system_prompt() -> str:
    return (
        "You are Code Chuckles, a friendly chatbot that ONLY tells programming-related jokes, puns, "
        "one-liners, and light-hearted humorous takes on code, debugging, languages, tools, version control, "
        "AI, regex, and dev life. Keep jokes safe-for-work and non-offensive. Be witty and kind.\n\n"
        "Guidelines:\n"
        "- Keep responses concise (1–3 sentences) unless asked for more.\n"
        "- If the request is vague, ask for a topic or language preference.\n"
        "- Tailor jokes to the user's prompt when possible.\n"
        "- Avoid providing non-joke factual content unless it enhances the humor."
    )

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []  # store only user/assistant messages for display and history

def render_chat_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def generate_response(client: OpenAI, model: str, temperature: float, user_input: str) -> str:
    system_prompt = build_system_prompt()
    # Prepare messages for API: system + history + latest user
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(st.session_state.messages)
    api_messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=model,  # "gpt-4" or "gpt-3.5-turbo"
        messages=api_messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

# ---------------------------
# Streamlit App
# ---------------------------

def main():
    st.set_page_config(page_title="Code Chuckles – Programming Joke Bot", page_icon="💻")
    st.title("Code Chuckles 🤖💡")
    st.caption("A friendly chatbot that tells programming jokes.")

    init_session_state()

    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        model = st.selectbox(
            "Model",
            options=["gpt-4", "gpt-3.5-turbo"],
            index=0,
            help="Choose the OpenAI model for joke generation."
        )
        temperature = st.slider(
            "Humor Randomness",
            min_value=0.2,
            max_value=1.2,
            value=0.8,
            step=0.1,
            help="Higher = more playful and surprising jokes."
        )
        if st.button("Clear chat"):
            st.session_state.messages = []
            st.experimental_rerun()

        st.markdown("---")
        st.markdown("Tip: Ask for jokes about specific languages, tools, or bugs!")

    # Render history
    render_chat_history()

    # Chat input
    user_input = st.chat_input("Ask for a programming joke (e.g., 'JavaScript closures', 'Git mishaps')")

    if user_input:
        # Show the user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Create OpenAI client
        client = OpenAI()

        try:
            bot_reply = generate_response(client, model=model, temperature=temperature, user_input=user_input)
        except Exception as e:
            bot_reply = "Oops! I ran into an error while fetching that joke. Please try again."

        # Show the assistant response
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        # Persist messages
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

if __name__ == "__main__":
    main()