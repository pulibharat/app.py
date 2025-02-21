



import google.generativeai as genai
import streamlit as st

genai.configure(api_key="AIzaSyDBx7bWJqgFu1BJyi5RZNNpGc54cqxT8Ms")

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",  
    generation_config=generation_config,
)

st.title("AI Disease Image Analysis")
st.subheader("Upload a disease image, and the AI will analyze it in-depth and provide detailed insights.")

# Upload file
uploaded_file = st.file_uploader("Upload a Disease Image", type=["jpeg", "jpg", "png"])

if uploaded_file:

    with open("uploaded_image.jpeg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Upload the image to Gemini
    uploaded_image = upload_to_gemini("uploaded_image.jpeg", mime_type="image/jpeg")

    # Get a user question for in-depth analysis
    user_question = st.text_input("Ask a detailed question about the image:", 
                                  "Please analyze this image and provide detailed information about the disease, including symptoms, causes, diagnosis, treatment, and prognosis.")

    if user_question:
        # Constructing a detailed prompt to get in-depth analysis
        detailed_prompt = (
            f"Please analyze the image in detail and provide the following information:\n"
            f"1. What disease is depicted in the image?\n"
            f"2. What are the visible symptoms associated with this disease?\n"
            f"3. What are the potential causes or risk factors for this disease?\n"
            f"4. How is this disease diagnosed by healthcare professionals?\n"
            f"5. What are the common treatment options for this disease?\n"
            f"6. What are the possible complications associated with this disease?\n"
            f"7. What is the prognosis or expected outcome for patients with this disease?\n"
        )

    
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        uploaded_image,
                        f"{detailed_prompt}\n",  
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "This appears to be an image of a specific disease. I will provide a detailed analysis based on the features visible in the image.\n",  # Default response
                    ],
                },
            ]
        )

        
        response = chat_session.send_message(detailed_prompt)

        
        colored_response = response.text.replace("disease", '<span style="color:red;">disease</span>')
        colored_response = colored_response.replace("treatment", '<span style="color:blue;">treatment</span>')

        
        st.markdown(f"AI Response: {colored_response}", unsafe_allow_html=True)
else:
    st.write("Please upload a disease image to get started.")
