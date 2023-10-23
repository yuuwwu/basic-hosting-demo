import datetime
import logging
from logging.config import fileConfig
import onnxruntime as rt
from prediction_service.core.fastapi_service import FastAPIServiceBase, FastAPIStateEnum
from prediction_service.query_service.schema import PostQueryRequest, PostQueryResponse
from prediction_service.query_service.utils import download_file_async

fileConfig("logging.ini")
LOGGER = logging.getLogger()
LOGGER_PREFIX = "QUERY_SERVICE"


class QueryService(FastAPIServiceBase):
    """
    Service to return top k predictions for a given query
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_url = (
            "https://gww-ds-mldevops.s3.amazonaws.com/pipeline_tfidfnb.onnx"
        )
        self.mode_dir = (
            "prediction_service/query_service/data/model/pipeline_tfidfnb.onnx"
        )
        self.model = None

    async def initialize(self):
        """
        Service initialization, load model, init model
        """
        LOGGER.info(
            f"{LOGGER_PREFIX} - {self.__class__.__name__}.initialize method called."
        )
        self.app.add_api_route(path="/predict", endpoint=self.predict, methods=["POST"])

        await self.load_model()
        self.model = rt.InferenceSession(self.mode_dir)

    async def load_model(self):
        """
        Load model from S3 url.
        """
        try:
            await download_file_async(url=self.model_url, destination=self.mode_dir)
        except Exception:
            self.api_state = FastAPIStateEnum.UNHEALTHY
            LOGGER.error(f"{LOGGER_PREFIX} - Failed to load model", exc_info=True)
            raise

    async def predict(self, user_request: PostQueryRequest) -> PostQueryResponse:
        """
        Run prediction on the model and return top k predictions based on user request.

        Args:
            user_request (PostQueryRequest): User request object with query and top_k.
        Returns:
            PostQueryResponse: Response object with query, predicted cats and probas.
        """
        query = user_request.query
        top_k = user_request.top_k
        model_inputs = {"input": [[query]]}

        start = datetime.datetime.now()

        try:
            pred_onnx = self.model.run(None, model_inputs)
            pred_onnx_proba_dict = pred_onnx[1][0]
            sorted_pred_onnx_proba_dict = sorted(
                pred_onnx_proba_dict.items(), key=lambda x: x[1], reverse=True
            )
            cats = [i[0] for i in sorted_pred_onnx_proba_dict[:top_k]]
            probas = [i[1] for i in sorted_pred_onnx_proba_dict[:top_k]]
            duration_ms = (datetime.datetime.now() - start).total_seconds() * 1000
            LOGGER.info(
                f"{LOGGER_PREFIX} - Predicted in {duration_ms:.2f} ms, query {query},"
                f" top_k {top_k}, predicted cats {cats}, predicted proba {probas}"
            )

            return PostQueryResponse(query=query, cats=cats, probas=probas)
        except Exception as err:
            LOGGER.error(f"{LOGGER_PREFIX} - Failed to predict", exc_info=True)
            try:
                return self.default_error_response(error_message=f"{err}")
            except Exception:
                LOGGER.error(f"{LOGGER_PREFIX} - Failed to send error", exc_info=True)


query_svc = QueryService()
app = query_svc.app
