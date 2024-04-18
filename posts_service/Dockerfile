FROM golang:latest

COPY /posts_service /posts_service

COPY /proto /proto

RUN apt-get update && apt-get install --no-install-recommends --assume-yes protobuf-compiler

RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

RUN protoc --proto_path=/proto --go_out=/posts_service --go-grpc_out=/posts_service /proto/posts_service.proto
WORKDIR /posts_service
RUN go mod tidy
# posts_service.pb.go
# posts_service_grpc.pb.go
# CMD ["cat", "./proto/posts_service.pb.go"]
EXPOSE 80

RUN go build -o post_service ./cmd/app/main.go
CMD ["./post_service"]