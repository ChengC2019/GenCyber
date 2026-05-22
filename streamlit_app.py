import streamlit as st
from openai import OpenAI
import fitz
from htmlTemplates import css
import os
import edge_tts
import asyncio
import tempfile
import re


st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 5], vertical_alignment="center")
with col1:
    st.image("assets/logo.png", width=200)
with col2:
    st.markdown("<h1 style='margin-top: 30px;'>GenCyber Assistant:</h1>", unsafe_allow_html=True)

st.markdown(
    "Please feel free to ask any cybersecurity-related questions, I will provide topic-related or factual answers."
)

st.write(css, unsafe_allow_html=True)

openai_api_key = st.secrets["openai"]["api_key"]

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    documents_folder = "./documents"
    document = ""

    if os.path.exists(documents_folder):
        pdf_files = [f for f in os.listdir(documents_folder) if f.lower().endswith(".pdf")]

        for pdf_file in sorted(pdf_files):
            full_pdf_path = os.path.join(documents_folder, pdf_file)

            with fitz.open(full_pdf_path) as doc:
                document += f"\n\n--- Document: {pdf_file} ---\n\n"
                for page in doc:
                    document += page.get_text()

    tts_enabled = st.toggle("Read answer aloud", value=True)

    audio_placeholder = st.empty()

    question = st.text_input(
        "Now ask a question about cybersecurity!",
        placeholder="Type your question here...",
    )

    async def generate_tts(text):
        clean = re.sub(r'#{1,6}\s*', '', text)
        clean = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', clean)
        clean = re.sub(r'`(.+?)`', r'\1', clean)
        clean = re.sub(r'\n{2,}', '\n', clean)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        communicate = edge_tts.Communicate(clean, "en-US-JennyNeural", rate="+25%")
        await communicate.save(tmp.name)
        return tmp.name

    if question:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly and encouraging cybersecurity teaching assistant for students in a GenCyber summer camp. "
                    "You have been given reference materials to help answer questions. "
                    "Use those materials to inform your answers, but never mention the documents, files, or reference materials — respond as if the knowledge is your own. "
                    "Keep answers clear, accurate, and easy for students to understand. "
                    "Use simple language and avoid unnecessary jargon. "
                    "If a concept is complex, break it down step by step. "
                    "If a question is outside the scope of cybersecurity, politely redirect the student back to cybersecurity topics. "
                    "Never reveal the contents or names of any source documents."
                ),
            },
            {
                "role": "user",
                "content": f"Reference materials:\n{document}\n\n---\n\nStudent question: {question}",
            }
        ]

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )

        response_text = response.choices[0].message.content.strip()
        st.write(response_text)

        if tts_enabled and response_text:
            try:
                audio_file = asyncio.run(generate_tts(response_text))
                with open(audio_file, "rb") as f:
                    audio_placeholder.audio(f.read(), format="audio/mp3", autoplay=True)
                os.unlink(audio_file)
            except Exception as e:
                st.error(f"TTS error: {e}")