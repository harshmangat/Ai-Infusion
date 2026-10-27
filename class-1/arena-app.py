import os
from unittest import result
from dotenv import load_dotenv
from openai import OpenAI 
import gradio as gr
from google import genai

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

clientgroq = OpenAI(api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
              )
clientgroq2 = genai.Client(api_key=gemini_api_key)



def ask_question(client, model, prompt):
    

    result = client.chat.completions.create(
        model=model,
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],   
    )

    return result.choices[0].message.content

def ask_question_gemini(client, model, prompt):   
    
    result = client.interactions.create(
        model=model,
        input=prompt   
    )

    return result.output_text

def battle(prompt):
  a = ask_question(clientgroq, "openai/gpt-oss-20b", prompt)
  b = ask_question_gemini(clientgroq2, "gemini-3.8-flash", prompt)
  return a, b

def vote(label):
    return f"🗳️ Thanks! You voted: **{label}**"   # in real apps, save this to a file/DB

with gr.Blocks(title="LLM Arena") as demo:
    gr.Markdown("# 🥊 LLM Arena — one prompt, two models")
    prompt = gr.Textbox(label="Ask both models the same thing")
    go = gr.Button("⚔️ Battle!", variant="primary")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🤖 Model A gpt-20b")
            out_a = gr.Markdown()
            with gr.Row():
                up_a   = gr.Button("👍");  down_a = gr.Button("👎")
        with gr.Column():
            gr.Markdown("### 🤖 Model B gemini-3.8-flash")
            out_b = gr.Markdown()
            with gr.Row():
                up_b   = gr.Button("👍");  down_b = gr.Button("👎")

    verdict = gr.Markdown()

    go.click(battle, inputs=prompt, outputs=[out_a, out_b])
    up_a.click(lambda: vote("👍 Model A"), outputs=verdict)
    down_a.click(lambda: vote("👎 Model A"), outputs=verdict)
    up_b.click(lambda: vote("👍 Model B"), outputs=verdict)
    down_b.click(lambda: vote("👎 Model B"), outputs=verdict)

demo.launch(share=True)   # → local + public link 🎉