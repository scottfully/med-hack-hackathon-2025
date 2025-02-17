from dotenv import load_dotenv
import os
import io
import base64
import json

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
# import matplotlib.pyplot as plt

# Initialize Flask
app = Flask(__name__)
CORS(app)


load_dotenv()

# put the OPENAI_API_KEY in the .env file
openai.api_key = os.getenv('OPENAI_API_KEY')


def load_data():

    return """{
    "discharge to": "Home",
    "medications": [
        "Start Ozempic 0.25mg for 4 weeks, then increase to 0.5mg for 4 weeks, then to 0.75mg for 4 weeks if there are no side effects",
        "Reduce Optisulin to 22 units every night",
        "Continue other oral hypoglycaemics at the current dose"
    ],
    "follow ups": [
        "Review in 3 months",
        "Get blood tests done again",
        "Follow up with GP for diet advice",
        "Appointment with a podiatrist in 2 weeks"
    ],
    "home monitoring": [
        "Weigh yourself every week"
    ],
    "other": [
        "Given a pamphlet and script for Ozempic",
        "Diabetes Australia hotline number was given",
        "A diabetic nurse will educate you on how to use a glucometer next week"
    ]
}"""

#     return """{
#     "discharge to": "community heart failure service",
#     "medications": [
#         "Stopped Hydrochlorthiazde",
#         "Started Amiodarone",
#         "Started Metoporlol",
#         "Started Empagliozin"
#     ],
#     "follow ups": [
#         "Referral to heart function clinic in 4 weeks with ECHO done prior",
#         "GP review for renal function in one week with blood test done prior"
#     ],
#     "home monitoring": ["Fluid restriction to 1.5 Litres","daily weight monitoring"],
#     "other": ["Cardio rehab program"]
# }"""

#     return """{
#     "discharge to": "None",
#     "medications": [
#         "Stopped Hydrochlorothiazide.",
#         "Started Spironolactone."
#     ],
#     "follow ups": [
#         "Visit GP in a week with repeated chest X-ray and urine test done prior.",
#         "Respiratory clinic review in 6 weeks with respiratory function test and high-resolution chest CT scan done prior."
#     ],
#     "home monitoring": ["None"],
#     "other": ["None"]
# }"""





#     return """{
#   "medicine_start": ["spironolactone"],
#   "medicine_stop": ["hydrochlorothiazide"],
#   "next_consultation": [
#     {
#       "when": "in 7 days",
#       "where": "GP clinic",
#       "with_who": "GP",
#       "tests_to_be_done": ["chest X-ray", "urine test"]
#     },
#     {
#       "when": "in 42 days",
#       "where": "respiratory clinic",
#       "with_who": "respiratory specialist",
#       "tests_to_be_done": ["respiratory function test", "High Resolution Chest CT scan"]
#     }
#   ]
# }"""



@app.route('/')
def home():
    return render_template('frontend.html')
    # return 'Flask app is running'

@app.route('/infographic')
def infographic():
    json_text = load_data()  # Load JSON data

    # Convert the JSON text to a Python dictionary
    data = json.loads(json_text)

    # print(render_template('infographic.html', data=data))
    # exit()
    return render_template('infographic.html', data=data)


@app.route('/generate-infographics', methods=['POST'])
def generate_infographics():
    data = request.get_json()
    text = data.get('text', '')  

    # Discharge summary data
    discharge_data = {
        "discharge_to": "Home",
        "pills": [
            {"drug_name": "Spironolactone 25mg", "status": "increase", "stop_date": None},
            {"drug_name": "Telmisartan 40mg", "status": "decrease", "stop_date": None},
            {"drug_name": "Amoxicillin 1g", "status": "stop_on_date", "stop_date": "2025-02-20"}
        ],
        "gp_followup": {
            "date_in_days": 7,
            "medication_to_followup": "Blood Pressure Medication"
        },
        "clinic_followup": {
            "repeat_bloods_date": "2025-03-01",
            "repeat_imaging_date": "2025-03-10"
        },
        "home_monitoring": [
            {"monitoring_type": "BSLs", "frequency": "Twice daily"},
            {"monitoring_type": "Blood pressure", "frequency": "Once daily"},
            {"monitoring_type": "Weight", "frequency": "Weekly"},
            {"monitoring_type": "Fever", "frequency": "If symptomatic"}
        ]
    }

    if not text:
        return jsonify({'error': 'No text provided'}), 400
    

    # "content": f"""Convert this discharge summary to structured JSON format {text} 
    #                 discharge_to: string,                                              
    #                 pills:
    #                 [
    #                     drug_name: string               
    #                     status: (stop / increase / decrease / stop_on_date)
    #                     stop_date: date (optional if Stop On Date)
    #                 ],
    #                 gp_followup:
    #                 {{
    #                     date_in_days: integer
    #                     medication_to_followup: string
    #                 }},
    #                 clinic_followup:
    #                 {{
    #                     repeat_bloods_date: date
    #                     repeat_imaging_date: date
    #                 }},
    #                 home_monitoring:
    #                 [
    #                     monitoring_type: (BSLs, blood pressure, weight, fever)
    #                     frequency: string
    #                 ] only follow the above schema in the output
    #             """

    # Step 1: Generate structured JSON output using OpenAI API
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You must convert doctor discharge summaries to a more simple form that can be read by patients and in a structured JSON output.\n\n"
            }, {
                "role": "user",
                "content": f"""Summarise the discharge summary to a format we use in simple terms. 
Rules:
Make sure you use the real names of specialists and services like GP and Respiratory clinic and procedures are kept, this is important. 
Only summarise the explanation points. 
Try to explain this in simple terms.
Put the information into the following categories: "discharge to", "medications", "follow ups", "home monitoring", "other".
For each category the information should be one line per instruction. 
The medications should be 1 line for each medication and instructions. 
Do not include 2 medications in line line item.
If it mentions "done prior" or similar you must include this information.
If there is no reference to the category explicitly stated in "medications", "follow ups", "home monitoring", "other" just put a single ["None"] for "discharge to" just put "None". 
Output to a JSON format. 

{text}
                """
            }]
        )
        summary = response.choices[0].message.content.strip()  # Extract the structured summary (JSON)
    except Exception as e:
        return jsonify({'error': f'Error generating summary: {str(e)}'}), 500

    # Extract event-related data for visualization
    # try:
    #     events = ["Referral", "Medication Start", "Follow-up", "Test"]
    #     values = [discharge_data["gp_followup"]["date_in_days"], 4, 7, 3]  # Example dynamic data

    #     fig, ax = plt.subplots()
    #     ax.bar(events, values, color='skyblue')

    #     ax.set_title("Medical Event Overview")
    #     ax.set_xlabel("Events")
    #     ax.set_ylabel("Severity / Days")
    #     ax.set_ylim(0, max(values) + 1)  

    #     buf = io.BytesIO()
    #     plt.savefig(buf, format='png')
    #     buf.seek(0)

    #     img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    # except Exception as e:
    #     return jsonify({'error': f'Error generating infographic: {str(e)}'}), 500
    
    # if we return a json object we may not need to do this
    discharge_json_data = json.loads(summary)
    rendered_infographic = render_template('infographic_contents.html', data=discharge_json_data)
                    
    # 'images': [f"data:image/png;base64,{img_base64}"],

    # Step 3: Return the structured summary and infographic
    return jsonify({
        'summary': summary,
        'discharge_data': discharge_data,
        'infographic_html': rendered_infographic
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

