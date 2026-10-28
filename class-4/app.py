import gradio as gr

from pdf_chat import ask, build_index, open_index


state = {"db": None}

theme = gr.themes.Soft(
    primary_hue="teal",
    secondary_hue="cyan",
    neutral_hue="slate",
).set(
    body_background_fill="#edf7f6",
    body_text_color="#173b3b",
    block_background_fill="#ffffff",
    block_border_color="#d7e8e6",
    input_background_fill="#ffffff",
    input_border_color="#cbdedc",
    button_primary_background_fill="#087e82",
    button_primary_background_fill_hover="#06676b",
    button_primary_text_color="#ffffff",
)

custom_css = """
:root {
    color-scheme: light;
}

body,
.gradio-container {
    background: #edf7f6 !important;
    color: #173b3b !important;
}

.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 28px 20px 40px !important;
}

#app-header {
    background: linear-gradient(125deg, #087e82 0%, #14515f 100%);
    border: 0;
    border-radius: 24px;
    box-shadow: 0 16px 36px rgba(20, 81, 95, 0.18);
    color: #ffffff;
    margin-bottom: 20px;
    padding: 28px 34px;
}

#app-header h1 {
    color: #ffffff;
    font-size: clamp(2rem, 4vw, 3rem);
    letter-spacing: -0.04em;
    margin: 4px 0 10px;
}

#app-header p {
    color: #d7f0ed;
    font-size: 1rem;
    margin-bottom: 0;
}

#upload-panel,
#chat-panel {
    background: #ffffff;
    border: 1px solid #d7e8e6;
    border-radius: 20px;
    box-shadow: 0 10px 28px rgba(31, 74, 73, 0.08);
    padding: 20px;
}

#upload-panel h2,
#chat-panel h2 {
    color: #174e50;
    letter-spacing: -0.02em;
}

#upload-panel > div {
    background-color: #ffffff;
}

#upload-status {
    background: #f0f8f7;
    border: 1px solid #dcecea;
    border-radius: 14px;
    padding: 12px 14px;
}

#workspace {
    align-items: stretch;
    gap: 18px;
}

button.primary {
    background: #087e82 !important;
    border-color: #087e82 !important;
}

button.primary:hover {
    background: #06676b !important;
}

@media (max-width: 700px) {
    .gradio-container {
        padding: 16px 12px 28px !important;
    }

    #app-header {
        border-radius: 18px;
        padding: 22px;
    }

    #upload-panel,
    #chat-panel {
        border-radius: 16px;
        padding: 14px;
    }
}
"""


def upload(document_paths):
    if not document_paths:
        return "Select one or more PDF or HTML files to add to your notes."

    db, file_names, chunk_count = build_index(document_paths)
    state["db"] = db
    names = "\n".join(f"- {name}" for name in file_names)
    return (
        f"Added **{len(file_names)} file(s)** as {chunk_count} searchable text "
        "chunks. Previously indexed files are kept in the local ChromaDB.\n\n"
        f"{names}"
    )


def chat(message, history):
    if not message or not message.strip():
        return "Enter a question about your uploaded files."

    if state["db"] is None:
        state["db"] = open_index()

    stored_documents = state["db"].get(limit=1)
    if not stored_documents["ids"]:
        return "Upload one or more PDF or HTML files before asking a question."

    return ask(state["db"], message)


with gr.Blocks(title="Chat with your notes") as demo:
    with gr.Column(elem_id="app-header"):
        gr.Markdown(
            "# Chat with your notes\n"
            "A calm, private workspace for exploring everything in your "
            "uploaded notes."
        )

    with gr.Row(elem_id="workspace"):
        with gr.Column(scale=1, elem_id="upload-panel"):
            gr.Markdown("## Add your files")
            gr.Markdown(
                "Upload one or more PDF or HTML files. They stay in your local "
                "notes collection for future questions."
            )
            document = gr.File(
                label="PDF or HTML files",
                file_types=[".pdf", ".html", ".htm"],
                file_count="multiple",
                type="filepath",
            )
            status = gr.Markdown(elem_id="upload-status")
            document.change(upload, inputs=document, outputs=status)

        with gr.Column(scale=2, elem_id="chat-panel"):
            gr.Markdown("## Ask your notes")
            gr.ChatInterface(fn=chat)


if __name__ == "__main__":
    demo.launch(share=False, theme=theme, css=custom_css)
