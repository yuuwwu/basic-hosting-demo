from prediction_service.query_service.service import query_svc
from prediction_service.core.fastapi_service import FastAPIServiceBase


class PredictionAPI(FastAPIServiceBase):
    """

    Paths:
        - /api/v1/query: Query Service
    """

    async def initialize(self):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mount("/api/v1/query", query_svc, "Query Service")
        # mount other services here if needed


prediction_service = PredictionAPI()
app = prediction_service.app
