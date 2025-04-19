from flask import Flask, request, jsonify
from modelAIFin import get_event_summary


# Initialize Flask app
app = Flask(__name__)



@app.route('/summary', methods=['GET'])
def summary_get():
    event_name = request.args.get("event_name", "")
    summary = get_event_summary(event_name)
    return f"<pre>{summary}</pre>"

# POST method: accepts JSON and returns JSON
@app.route('/api/summary', methods=['POST'])
def summary_post():
    data = request.get_json()
    event_name = data.get("event_name", "")
    summary = get_event_summary(event_name)
    return jsonify({
        "event_name": event_name,
        "summary": summary
    })

# Start the app
app.run()

