import streamlit as st
import tritonclient.http as httpclient
import numpy as np
import socket

# ---------- CONFIG ----------
TRITON_URL = "localhost:8000"  # Change if running on remote server
MODEL_NAME = "mistral-7b-gguf"
INPUT_NAME = "PROMPT"
OUTPUT_NAME = "OUTPUT"
TIMEOUT_SECONDS = 300  # Triton inference timeout

# ---------- SET SOCKET TIMEOUT (fallback for old Triton clients) ----------
socket.setdefaulttimeout(TIMEOUT_SECONDS)

# ---------- LOAD TRITON CLIENT ----------
@st.cache_resource
def load_client():
    return httpclient.InferenceServerClient(
        url=TRITON_URL,
        verbose=False
        # Note: `timeout` is not supported directly in some versions
    )

# ---------- INFERENCE FUNCTION ----------
def query_triton(prompt: str) -> str:
    try:
        client = load_client()

        input_tensor = httpclient.InferInput(INPUT_NAME, [1], "BYTES")
        input_tensor.set_data_from_numpy(np.array([prompt.encode("utf-8")], dtype=object))

        output_tensor = httpclient.InferRequestedOutput(OUTPUT_NAME)

        result = client.infer(
            model_name=MODEL_NAME,
            inputs=[input_tensor],
            outputs=[output_tensor]
        )

        response = result.as_numpy(OUTPUT_NAME)[0].decode("utf-8")
        return response
    except Exception as e:
        return f"[Error] {e}"

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="🧠 Mistral 7B Chatbot", layout="centered")
st.title("🤖 Mistral 7B Chatbot")
st.caption("Powered by NVIDIA Triton Inference Server")

# ---------- INIT SESSION STATE ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- INPUT FORM ----------
with st.form("chat_form"):
    user_input = st.text_area("You:", height=100, placeholder="Ask me anything...")
    submitted = st.form_submit_button("Send")

# ---------- HANDLE SUBMISSION ----------
if submitted and user_input.strip():
    with st.spinner("Mistral is thinking..."):
        reply = query_triton(user_input.strip())
        st.session_state.chat_history.append(("user", user_input.strip()))
        st.session_state.chat_history.append(("bot", reply.strip()))

# ---------- DISPLAY CHAT ----------
for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 Mistral:** {message}")
