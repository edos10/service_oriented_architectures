FROM golang:latest

COPY /stat_service /stat_service

WORKDIR /stat_service
RUN go mod tidy

EXPOSE 5002

RUN go build -o stat_service ./cmd/main.go
CMD ["./stat_service"]