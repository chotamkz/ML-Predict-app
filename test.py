import sys

import grpc
sys.path.append("proto")
from proto import prediction_pb2_grpc, prediction_pb2

def run():
    with grpc.insecure_channel('localhost:5001') as channel:
        stub = prediction_pb2_grpc.PredictionServiceStub(channel)

        # Создаем запрос
        request = prediction_pb2.PredictionRequest(
            operating_system=70,
            analysis_of_algorithm=71,
            programming_concept=86,
            software_engineering=69,
            computer_network=92,
            applied_mathematics=99,
            computer_security=65,
            hackathons_attended=2,
            topmost_certification="MongoDB Certified DBA",
            personality="Extravert",
            management_technical="Management",
            leadership="Yes",
            team="No",
            self_ability="Yes"
        )

        response = stub.Predict(request)
        print("Predicted track:", response.predicted_track)

if __name__ == '__main__':
    run()
