import asyncio
import logging
from concurrent import futures
from dataclasses import dataclass
from typing import Dict, Any, Tuple
import grpc
from grpc_reflection.v1alpha import reflection
from grpc.aio import server as aio_server
import joblib
import numpy as np
import sys
from pathlib import Path

from cache import PredictionCache
from config import Settings

sys.path.append(str(Path("./proto").absolute()))
from proto import prediction_pb2_grpc, prediction_pb2

settings = Settings()
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

cache = PredictionCache(settings.CACHE_TTL)


@dataclass
class ModelContainer:
    prediction_model: Any
    encoders: Dict[str, Any]
    version: str

    @classmethod
    def load_models(cls, version: str) -> 'ModelContainer':
        try:
            return cls(
                prediction_model=joblib.load(settings.MODELS_DIR / 'student_track_prediction_model.pkl'),
                encoders={
                    'certification': joblib.load(settings.MODELS_DIR / 'certification_encoder.pkl'),
                    'personality': joblib.load(settings.MODELS_DIR / 'personality_encoder.pkl'),
                    'management_technical': joblib.load(settings.MODELS_DIR / 'management_technical_encoder.pkl'),
                    'yes_no': joblib.load(settings.MODELS_DIR / 'yes_no_encoder.pkl')
                },
                version=version
            )
        except Exception as e:
            logger.error(f"Ошибка при загрузке моделей: {e}")
            raise


class PredictionService(prediction_pb2_grpc.PredictionServiceServicer):
    def __init__(self, model_container: ModelContainer):
        self.model_container = model_container

    def _prepare_features(self, request) -> Tuple:
        encoders = self.model_container.encoders
        features = (
            request.operating_system,
            request.analysis_of_algorithm,
            request.programming_concept,
            request.software_engineering,
            request.computer_network,
            request.applied_mathematics,
            request.computer_security,
            request.hackathons_attended,
            encoders['certification'].transform([request.topmost_certification])[0],
            encoders['personality'].transform([request.personality])[0],
            encoders['management_technical'].transform([request.management_technical])[0],
            encoders['yes_no'].transform([request.leadership])[0],
            encoders['yes_no'].transform([request.team])[0],
            encoders['yes_no'].transform([request.self_ability])[0]
        )
        return features

    async def Predict(self, request, context):
        try:
            features = self._prepare_features(request)

            cache_hit, cached_result = cache.get(features)
            if cache_hit:
                logger.info("Использован результат из кэша")
                return prediction_pb2.PredictionResponse(predicted_track=cached_result)

            features_array = np.array(features).reshape(1, -1)
            prediction = self.model_container.prediction_model.predict(features_array)

            cache.set(features, prediction[0])

            logger.info(f"Предсказание выполнено успешно: {prediction[0]}")

            return prediction_pb2.PredictionResponse(predicted_track=prediction[0])

        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}")
            await context.set_code(grpc.StatusCode.INTERNAL)
            await context.set_details(f"Внутренняя ошибка сервера: {str(e)}")
            return prediction_pb2.PredictionResponse()


async def serve(model_container: ModelContainer):
    server = aio_server(futures.ProcessPoolExecutor(max_workers=settings.MAX_WORKERS))
    prediction_pb2_grpc.add_PredictionServiceServicer_to_server(
        PredictionService(model_container), server
    )

    service_names = (
        prediction_pb2.DESCRIPTOR.services_by_name['PredictionService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    server_addr = f'[::]:{settings.SERVER_PORT}'
    server.add_insecure_port(server_addr)

    logger.info(f"Запуск сервера на {server_addr}")
    await server.start()
    await server.wait_for_termination()


async def main():
    try:
        model_container = ModelContainer.load_models(settings.MODEL_VERSION)
        await serve(model_container)
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске сервера: {e}")
        sys.exit(1)


if __name__ == '__main__':
    logger.info("Запуск ML сервера")
    asyncio.run(main())

# docker build -t ml-api .
# docker run -d -p 5001:5001 ml-api
# python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/prediction.proto
