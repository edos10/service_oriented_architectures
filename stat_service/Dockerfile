FROM golang:latest

COPY /stat_service /stat_service

COPY /proto /proto

RUN apt-get update && apt-get install --no-install-recommends --assume-yes protobuf-compiler

RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

RUN protoc --proto_path=/proto --go_out=/stat_service --go-grpc_out=/stat_service /proto/stat_service.proto
WORKDIR /stat_service
RUN go mod tidy
# posts_service.pb.go
# posts_service_grpc.pb.go
# CMD ["cat", "./proto/posts_service.pb.go"]
EXPOSE 81

RUN go build -o stat_service ./cmd/main.go
CMD ["./stat_service"]