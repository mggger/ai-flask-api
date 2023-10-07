import openai
from config import Config
import uuid
import tempfile
import zipfile
import os
import logging

from embedchain.config import CustomAppConfig, ChatConfig
from embedchain.models import Providers, EmbeddingFunctions
from embedchain.models.data_type import DataType
from embedchain import App

class EmbeddingTrainer:
    def __init__(self):
        # 配置OpenAI API密钥
        import os
        openai.api_key = Config['openai_api_key']
        os.environ['OPENAI_API_KEY'] = Config['openai_api_key']

        # 配置代理
        if Config['is_local']:
            openai.proxy = 'http://localhost:1087'

        # 设置日志记录器
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # 初始化Embedchain应用
        chroma_settings = {
            "anonymized_telemetry": False,
            "allow_reset": True
        }

        config = CustomAppConfig(log_level='INFO',
                                 collection_name='default',
                                 provider=Providers.OPENAI,
                                 embedding_fn=EmbeddingFunctions.OPENAI,
                                 chroma_settings=chroma_settings
                                 )
        self.bot = App(config)

    def chat(self, query, history, model_id=None):
        if model_id is not None:
            chatConfig = ChatConfig(model=model_id)
        else:
            chatConfig = ChatConfig()

        if len(history) > 0:
            chatConfig.set_history(history)

        response = self.bot.chat(query, chatConfig)

        self.logger.info(f"Chat response: {response}")

        return response

    def train_url(self, url):
        self.logger.info(f"Training URL: {url}")
        return self.bot.add(url, metadata={'url': url}, data_type=DataType.WEB_PAGE)

    def train_file(self, file_name, content):
        self.logger.info(f"Training file: {file_name}")

        if '.' in file_name:
            _type = file_name.split(".")[-1]
        else:
            _type = "unknown"

        if _type == 'pdf':
            file_path = f"{self.get_uuid()}.pdf"
            with open(file_path, 'wb') as f:
                f.write(content)
            self.train_pdf(file_path)
            os.remove(file_path)

        elif _type == "docx" or _type == "doc":
            file_path = f"{self.get_uuid()}.docx"
            with open(file_path, 'wb') as f:
                f.write(content)
            self.train_docx(file_path)
            os.remove(file_path)

        elif _type == "zip":
            file_path = f"{self.get_uuid()}.zip"
            with open(file_path, 'wb') as f:
                f.write(content)
            self.train_zip(file_path)
            os.remove(file_path)

        else:
            file_path = f"{self.get_uuid()}.{_type}"
            with open(file_path, 'wb') as f:
                f.write(content)
            self.train_any(file_path)
            os.remove(file_path)

    def train_any(self, filename):
        self.logger.info(f"Training file: {filename}")
        return self.bot.add(filename, DataType.TEXT)

    def train_zip(self, path):
        self.logger.info(f"Training ZIP file: {path}")
        extracted_files = self.extract_zip_files(path)
        for extracted_file in extracted_files:
            self.recursively_train_files_in_directory_or_file(extracted_file)

    def recursively_train_files_in_directory_or_file(self, entry_path):
        try:
            if os.path.isfile(entry_path):
                if entry_path.endswith('.pdf'):
                    self.train_pdf(entry_path)
                elif entry_path.endswith('.docx') or entry_path.endswith('.doc'):
                    self.train_docx(entry_path)
                else:
                    self.train_any(entry_path)
                os.remove(entry_path)
            elif os.path.isdir(entry_path):
                for root, _, files in os.walk(entry_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        self.recursively_train_files_in_directory_or_file(file_path)
        except Exception as e:
            self.logger.error(f"An error occurred while processing file: {entry_path}")
            self.logger.error(f"Error message: {str(e)}")

    def extract_zip_files(self, zip_path):
        self.logger.info(f"Extracting ZIP file: {zip_path}")
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        extracted_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)]
        return extracted_files

    def train_pdf(self, path):
        self.logger.info(f"Training PDF file: {path}")
        return self.bot.add(path, DataType.PDF_FILE)

    def train_docx(self, path):
        self.logger.info(f"Training DOCX file: {path}")
        return self.bot.add(path, DataType.DOCX)

    def train_text(self, content, filename='local'):
        self.logger.info("Training text data")
        return self.bot.add_local(content, DataType.TEXT, metadata={'url': filename})

    def get_uuid(self):
        random_uuid = uuid.uuid4()
        return str(random_uuid)
