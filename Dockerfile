FROM python:3.11-slim

LABEL description="央视频全频道直播代理 v7.4（纯 Python，单端口版）"

ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    YSP_DATA_DIR=/app/data

WORKDIR /app

COPY ysp-live.py ./

RUN mkdir -p /app/data

VOLUME ["/app/data"]

EXPOSE 8767

CMD ["python3", "-u", "ysp-live.py"]
