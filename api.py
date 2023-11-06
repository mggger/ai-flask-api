from flask import Flask, request, jsonify
import base64
import logging

from embedding import EmbeddingTrainer
from fine_tuning import FineTuning

app = Flask(__name__)
app.embeddings = EmbeddingTrainer()

# 设置日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/chat", methods=['POST'])
def chat_api_handler():
    data = request.json
    question = data.get("question", "")
    history = data.get("history", [])
    model_id = data.get("model_id", None)

    logger.info(f"Received chat request with question: {question}")

    response = app.embeddings.chat(question, history, model_id)

    logger.info(f"Generated response: {response}")

    return jsonify({"answer": response})


@app.route("/fine_tuning", methods=['POST'])
def fine_tuning_handler():
    data = request.json
    file_content_base64 = data.get("content")
    file_content = base64.b64decode(file_content_base64)

    n_epochs = data.get("n_epochs", None)

    logger.info("Received fine-tuning request")

    ft = FineTuning(n_epochs)
    model_id = ft.run(file_content)

    logger.info(f"Fine-tuning completed. Model ID: {model_id}")

    return jsonify({"model_id": model_id})


@app.route("/embeddings/train", methods=['POST'])
def train_handler():
    data = request.json

    selected_files = data.get("files", [])
    url_input = data.get("url", "")
    text = data.get("text", "")
    model_id = data.get("model_id")

    logger.info("Received training request")

    em = app.embeddings

    if model_id:
        em = EmbeddingTrainer(model_id)

    for file_data in selected_files:
        file_name = file_data.get("name")
        file_content_base64 = file_data.get("content")
        file_content = base64.b64decode(file_content_base64)
        em.train_file(file_name, file_content)

    if url_input != "":
        em.train_url(url_input)

    if text != "":
        em.train_text(text, "local")

    logger.info("Training completed successfully")

    return jsonify({"res": "Training started successfully"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
