from concurrent import futures

from flask import Flask
import joblib
import numpy as np
import grpc

import sys

from grpc_reflection.v1alpha import reflection

sys.path.append("./proto")
from proto import prediction_pb2_grpc, prediction_pb2

app = Flask(__name__)

model = joblib.load('models/student_track_prediction_model.pkl')
certification_encoder = joblib.load('models/certification_encoder.pkl')
personality_encoder = joblib.load('models/personality_encoder.pkl')
management_technical_encoder = joblib.load('models/management_technical_encoder.pkl')
yes_no_encoder = joblib.load('models/yes_no_encoder.pkl')


class PredictionServiceServicer(prediction_pb2_grpc.PredictionServiceServicer):
    def Predict(self, request, context):
        print("получен запрос")
        try:
            features = [
                request.operating_system,
                request.analysis_of_algorithm,
                request.programming_concept,
                request.software_engineering,
                request.computer_network,
                request.applied_mathematics,
                request.computer_security,
                request.hackathons_attended,
                certification_encoder.transform([request.topmost_certification])[0],
                personality_encoder.transform([request.personality])[0],
                management_technical_encoder.transform([request.management_technical])[0],
                yes_no_encoder.transform([request.leadership])[0],
                yes_no_encoder.transform([request.team])[0],
                yes_no_encoder.transform([request.self_ability])[0]
            ]

            features = np.array(features).reshape(1, -1)
            prediction = model.predict(features)

            return prediction_pb2.PredictionResponse(predicted_track=prediction[0])
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return prediction_pb2.PredictionResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    prediction_pb2_grpc.add_PredictionServiceServicer_to_server(PredictionServiceServicer(), server)

    SERVICE_NAMES = (
        prediction_pb2.DESCRIPTOR.services_by_name['PredictionService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)


    server.add_insecure_port('[::]:5001')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    print("Server-ml started")
    serve()
# docker build -t ml-api .
# docker run -d -p 5001:5001 ml-api
#python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/prediction.proto