import gradio as gr
# Added: import the PDF indexing and question-answering functions.
from pdf_chat import ask, build_index


state = {"db": None}                    # ① remember the index across turns

# Added: accept a PDF or HTML upload and index its contents.
def upload(document_path):
    if not document_path:
        return "Please upload a PDF or HTML file first."
    state["db"] = build_index(document_path)
    return "✅ Document indexed! Ask me anything about it."

def chat(message, history):
    if state["db"] is None:
        return "Please upload a PDF or HTML document first 📄"
    return ask(state["db"], message)

# Added: support uploading PDF and HTML files as filesystem paths.
with gr.Blocks(title="📄 Chat with your document") as demo:
    gr.Markdown("## 📄 Chat with your PDF or HTML document (powered by RAG)")
    document = gr.File(
        label="Upload a PDF or HTML file",
        file_types=[".pdf", ".html", ".htm"],
        type="filepath",
    )
    status = gr.Markdown()
    document.upload(upload, inputs=document, outputs=status)
    gr.ChatInterface(fn=chat)

demo.launch(share=True)  