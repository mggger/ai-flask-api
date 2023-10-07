import openai
from config import Config
import time
import logging

class FineTuning:
    def __init__(self):
        import os
        openai.api_key = Config['openai_api_key']
        os.environ['OPENAI_API_KEY'] = Config['openai_api_key']

        if Config['is_local']:
            openai.proxy = 'http://localhost:1087'

        # 设置日志记录器
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run(self, content):
        file_id = self.upload_file(content)
        model_id = self.create_model(file_id)
        return model_id

    def upload_file(self, content):
        self.logger.info("Uploading file for fine-tuning")

        upload_file = openai.File.create(
            file=content,
            purpose='fine-tune'
        )

        self.logger.info("File upload completed")

        return upload_file.id

    def create_model(self, file_id):
        self.logger.info("Creating fine-tuned model")

        job = openai.FineTuningJob.create(
            training_file=file_id,
            model="gpt-3.5-turbo",
        )

        start_time = time.time()
        status = openai.FineTuningJob.retrieve(job.id).status

        while status != "succeeded":
            self.logger.info(f"Status=[{status}]... {time.time() - start_time:.2f}s")
            time.sleep(5)
            status = openai.FineTuningJob.retrieve(job.id).status

        model_id = openai.FineTuningJob.retrieve(job.id).fine_tuned_model

        self.logger.info("Fine-tuning completed. Model ID: %s", model_id)

        return model_id
