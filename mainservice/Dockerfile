FROM python:3.10-alpine

COPY ./mainservice ./mainservice

COPY ./proto ./proto

RUN pip install --no-cache-dir -r ./mainservice/requirements.txt

RUN python3 -m grpc_tools.protoc -I/proto --python_out=/mainservice/src/proto/ --pyi_out=/mainservice/src/proto/ --grpc_python_out=/mainservice/src/proto/ /proto/posts_service.proto

WORKDIR /mainservice
#CMD ["ls", "./src/proto"]
#CMD ["cat", "./src/proto/posts_service_pb2.py"]
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000"]
