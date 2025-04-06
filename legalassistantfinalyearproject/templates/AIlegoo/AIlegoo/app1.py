from flask import Flask, request, jsonify, render_template_string
from groq import Groq
import os

app = Flask(__name__)

# Set your API key here
os.environ["GROQ_API_KEY"] = "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"

client = Groq()

@app.route('/')
def home():
    return render_template_string(open('index.html').read())  # Serves the HTML file

@app.route('/chat', methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("userMessage")

    if user_message:
        prompt = f"Act as a legal assistant specializing in Indian law. A user is asking for legal advice regarding the following scenario: {user_message}. Please provide detailed steps, relevant laws, and actions the user should take, with each step clearly separated and easy to understand."

        # Send the dynamic prompt to the model
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[ 
                {"role": "system", "content": "Act as a legal assistant specializing in Indian law."},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        bot_reply = ""
        for chunk in completion:
            bot_reply += chunk.choices[0].delta.content or ""

        # Format the response to be rendered as HTML
        formatted_reply = f"""
        <b>Legal Advice for Your Scenario:</b><br><br>
        {bot_reply.replace('\n', '<br><br>')}
        """
        return jsonify({"reply": formatted_reply})
    
    return jsonify({"reply": "Sorry, I couldn't understand your message."})


if __name__ == "__main__":
    app.run(debug=True)
