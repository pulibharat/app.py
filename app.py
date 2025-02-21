import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for
import os

# Configure your Gemini API Key
genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your actual API key

# Flask application setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Make sure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to upload image to Gemini
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Set generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Set up the generative model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",  
    generation_config=generation_config,
)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Route for uploading the image
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpeg')
        file.save(filename)

        # Upload the image to Gemini
        uploaded_image = upload_to_gemini(filename, mime_type="image/jpeg")

        # Get a user question for in-depth analysis
        user_question = request.form.get('question', 'Please analyze this image and provide detailed information about the disease, including symptoms, causes, diagnosis, treatment, and prognosis.')

        # Constructing a detailed prompt
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

        # Start the AI chat session
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

        # Get the AI's response
        response = chat_session.send_message(detailed_prompt)

        # Return the response to the user
        colored_response = response.text.replace("disease", '<span style="color:red;">disease</span>')
        colored_response = colored_response.replace("treatment", '<span style="color:blue;">treatment</span>')

        return render_template('result.html', response=colored_response)

    return redirect(url_for('home'))

if __name__ == '__main__':
    # Don't run the server with `app.run()` in production
    # Gunicorn will take care of it
    app.run(debug=False)
