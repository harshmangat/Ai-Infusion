import gradio as gr
from agent import PRICES, WELCOME_MESSAGE, agent


def chat(message, history):
    # Gradio fills in `message` (newest) and `history` (past turns) for you.
    # Homework hint: pass `history` into your agent to give it memory!
    return agent(message)




chatbot = gr.Chatbot(
    value=[
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
        }
    ]
)


gr.ChatInterface(
    fn=chat,
    chatbot=chatbot,
    title="🛍️ Smart Shop Assistant",
    description="Ask me the price of shoes, hat, bag, shorts or pants — I'll look it up.",
).launch(share=True) 