from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

model = joblib.load('student_track_prediction_model.pkl')
certification_encoder = joblib.load('certification_encoder.pkl')
personality_encoder = joblib.load('personality_encoder.pkl')
management_technical_encoder = joblib.load('management_technical_encoder.pkl')
yes_no_encoder = joblib.load('yes_no_encoder.pkl')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json

        features = [
            data['Operating System'],
            data['Analysis of Algorithm'],
            data['Programming Concept'],
            data['Software Engineering'],
            data['Computer Network'],
            data['Applied Mathematics'],
            data['Computer Security'],
            data['Hackathons attended'],
            certification_encoder.transform([data['Topmost Certification']])[0],
            personality_encoder.transform([data['Personality']])[0],
            management_technical_encoder.transform([data['Management or technical']])[0],
            yes_no_encoder.transform([data['Leadership']])[0],
            yes_no_encoder.transform([data['Team']])[0],
            yes_no_encoder.transform([data['Self Ability']])[0]
        ]

        features = np.array(features).reshape(1, -1)
        prediction = model.predict(features)

        return jsonify({'predicted_track': prediction[0]})

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
#docker build -t ml-api .
#docker run -d -p 5001:5001 ml-api