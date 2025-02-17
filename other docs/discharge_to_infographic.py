from flask import Flask, render_template, json

app = Flask(__name__)

def load_data():
    return """{
  "medicine_start": ["spironolactone"],
  "medicine_stop": ["hydrochlorothiazide"],
  "next_consultation": [
    {
      "when": "in 7 days",
      "where": "GP clinic",
      "with_who": "GP",
      "tests_to_be_done": ["chest X-ray", "urine test"]
    },
    {
      "when": "in 42 days",
      "where": "respiratory clinic",
      "with_who": "respiratory specialist",
      "tests_to_be_done": ["respiratory function test", "High Resolution Chest CT scan"]
    }
  ]
}"""

@app.route('/infographic')
def home():
    data = load_data()  # Load JSON data
    return render_template('infographic.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
