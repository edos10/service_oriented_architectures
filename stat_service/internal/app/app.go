package app

import (
	"context"
	"fmt"
	"log"
	"net"
	"stat_service/internal/config"
	"stat_service/internal/kafka"
	"stat_service/internal/repository"
	"stat_service/proto"

	"go.uber.org/zap"
	"google.golang.org/grpc"
)

type AppServer struct {
	cfg                *config.Config
	server             *repository.GrpcServer
	kafkaConsumerLikes *kafka.KafkaConsumer
	kafkaConsumerViews *kafka.KafkaConsumer
	logger             *zap.Logger
}

func NewAppServer(cfg *config.Config, logger *zap.Logger) *AppServer {
	viewsDb, errCreate := repository.CreateDatabaseConnect("stat")
	likesDb, err := repository.CreateDatabaseConnect("stat")

	if err != nil || errCreate != nil {
		fmt.Println(err, errCreate)
	}

	consumeLikes := kafka.NewKafkaConsumer([]string{"127.0.0.1:9092"}, "likes", likesDb)
	consumeViews := kafka.NewKafkaConsumer([]string{"127.0.0.1:9092"}, "views", viewsDb)

	db, err := repository.CreateDatabaseConnect("stat")
	if err != nil {
		panic("unable to connect with db...")
	}

	a := &AppServer{
		cfg: cfg,
		server: &repository.GrpcServer{
			Db: db,
		},
		kafkaConsumerLikes: consumeLikes,
		kafkaConsumerViews: consumeViews,
		logger:             logger,
	}

	return a
}

func (a *AppServer) Run() {
	go func() {
		a.kafkaConsumerLikes.ConsumeLikes()
	}()

	go func() {
		a.kafkaConsumerViews.ConsumeViews()
	}()

	go func() {
		s := grpc.NewServer()
		proto.RegisterStatServiceServer(s, a.server)
		port, err := net.Listen("tcp", ":81")
		if err != nil {
			log.Fatalf("failed to listen: %v", err)
		}
		err = s.Serve(port)
		if err != nil {
			a.logger.Error("Failed to start grpc server", zap.Error(err))
		}
	}()
}

func (a *AppServer) Stop(ctx context.Context) {
	a.kafkaConsumerLikes.Close()
	a.kafkaConsumerViews.Close()
}
