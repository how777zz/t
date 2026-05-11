FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 先複製 requirements 以利層快取
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再複製專案內容
COPY . .

# 安裝本專案 package (CLI 用)
RUN pip install --no-cache-dir -e .

EXPOSE 8501

# 預設啟動 Streamlit Web App
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
