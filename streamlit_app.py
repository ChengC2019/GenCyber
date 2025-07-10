import streamlit as st
from openai import OpenAI
import fitz 
from htmlTemplates import css

# Show title and description.
uah_logo_url = "https://www.uah.edu/images/administrative/communications/logo/uah-logo.svg"

st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 20px !important;
        }

    </style>
""", unsafe_allow_html=True)

# Create two columns: one for the logo, one for the title
col1, col2 = st.columns([1, 6])  # Adjust ratio to size preference

with col1:
    st.image(uah_logo_url, width=300)
with col2:
    st.title("GenCyber Assistant:")
st.markdown(
    "Please feel free to ask any cybersecurity-related questions, I will provide topic-related or factual answers."
)
st.write(css, unsafe_allow_html=True)


# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets["openai"]["api_key"]
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    # uploaded_file = st.file_uploader(
    #     "Upload a PDF document", type="pdf"
    # )
    
    # Path to your local PDF file
    pdf_path = "./CSResource.pdf"

    # Read the PDF
    with fitz.open(pdf_path) as doc:
        document = ""
        for page in doc:
            document += page.get_text()

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about cybersecurity!",
        placeholder="Type your question here...",
        # disabled=not uploaded_file,
    )

    if question:
        # Process the uploaded file and question.
        # document = uploaded_file.read().decode()
        # with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        #     document = ""
        #     for page in doc:
        #         document += page.get_text()

        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
