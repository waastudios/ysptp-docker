FROM python:3.11-slim

LABEL description="央视频全频道直播代理 v6.2（纯 Python，单端口版）"

WORKDIR /app

COPY ysp-live.py ./

EXPOSE 8767

CMD ["python3", "ysp-live.py"]
