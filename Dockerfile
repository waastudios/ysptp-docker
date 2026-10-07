FROM python:3.12-alpine
ENV TZ=Asia/Shanghai     PYTHONUNBUFFERED=1     YSP_DATA_DIR=/app/data
RUN apk add --no-cache nodejs tzdata ca-certificates &&     cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime &&     echo "Asia/Shanghai" > /etc/timezone &&     mkdir -p /app /app/data
WORKDIR /app
COPY ysp-live.py /app/ysp-live.py
COPY epg_agg.py /app/epg_agg.py
COPY ysp-engine.js /app/ysp-engine.js
EXPOSE 8767
VOLUME ["/app/data"]
CMD ["python3", "/app/ysp-live.py", "8767"]
