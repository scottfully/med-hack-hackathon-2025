from dotenv import load_dotenv
import os
import json

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai

# Initialize Flask
app = Flask(__name__)
CORS(app)


load_dotenv()

# put the OPENAI_API_KEY in the .env file
openai.api_key = os.getenv('OPENAI_API_KEY')

#  JSON Schema format
# {
#   "type": "object",
#   "properties": {
#     "discharge_to": {
#       "type": "string"
#     },
#     "medications": {
#       "type": "array",
#       "items": {
#         "type": "string"
#       }
#     },
#     "follow_ups": {
#       "type": "array",
#       "items": {
#         "type": "string"
#       }
#     },
#     "home_monitoring": {
#       "type": "array",
#       "items": {
#         "type": "string"
#       }
#     },
#     "other": {
#       "type": "array",
#       "items": {
#         "type": "string"
#       }
#     }
#   },
#   "required": ["discharge_to", "medications", "follow_ups", "home_monitoring", "other"]
# }

SYSTEM_AI_PROMPT = "You must convert doctor discharge summaries to a more simple form that can be read by patients and in a structured JSON output.\n\n"

AI_PROMPT = """Summarise the discharge summary to a format we use in simple terms. 
Rules:
Make sure you use the real names of specialists and services like GP and Respiratory clinic and procedures are kept, this is important. 
Only summarise the explanation points. 
Try to explain this in simple terms.
Put the information into the following categories: "discharge_to", "medications", "follow_ups", "home_monitoring", "other".
For each category the information should be one line per instruction. 
The medications should be 1 line for each medication and instructions.
If you see referred to you can put it in the other section 
Do not include 2 medications in line line item.
If it mentions "done prior" or similar you must include this information.
If there is no mention of discharge set the discharge_to to "Home".
If there is no reference to the category explicitly stated in "medications", "follow_ups", "home_monitoring", "other" just put a single ["None"] for "discharge_to" just put "None". 
Output to the following JSON format and only include the JSON and no extra text. the output should start with { and end with } and not "json":

{
    "discharge_to": string,
    "medications": [string],
    "follow_ups": [string],
    "home_monitoring": [string],
    "other": [string],

}
"""


@app.route('/')
def home():
    return render_template('frontend.html')


@app.route('/generate-infographics', methods=['POST'])
def generate_infographics():
    data = request.get_json()
    text = data.get('text', '')  

    if not text:
        return jsonify({'error': 'No text provided'}), 400
    

    # Step 1: Generate structured JSON output using OpenAI API
    try:
        response = openai.chat.completions.create(
            # model="gpt-4",
            model="gpt-4o",
            # model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": SYSTEM_AI_PROMPT
            }, {
                "role": "user",
                "content": f"""{AI_PROMPT} 

{text}
                """
            }]
        )

        summary = response.choices[0].message.content.strip()  # Extract the structured summary (JSON)
        # Debugging to show ChatGPT output
        print('Output: ' + summary)

    except Exception as e:
        return jsonify({'error': f'Error generating summary: {str(e)}'}), 500

    # if we return a json object we may not need to do this
    discharge_json_data = json.loads(summary)
    rendered_infographic = render_template('infographic_contents.html', data=discharge_json_data)
 
    # Step 3: Return the structured summary and infographic
    return jsonify({
        'summary': summary,
        'infographic_html': rendered_infographic
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

