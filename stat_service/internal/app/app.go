package app

import (
	"context"
	"fmt"
	"net/http"
	"stat_service/internal/kafka"
	"stat_service/internal/repository"

	"stat_service/internal/config"

	"go.uber.org/zap"
)

type AppServer struct {
	cfg                *config.Config
	server             *http.Server
	kafkaConsumerLikes *kafka.KafkaConsumer
	kafkaConsumerViews *kafka.KafkaConsumer
	logger             *zap.Logger
}

func NewAppServer(cfg *config.Config, logger *zap.Logger) *AppServer {
	address := fmt.Sprintf(":%d", cfg.Http.Port)

	viewsDb, errCreate := repository.CreateDatabaseConnect("stat")
	likesDb, err := repository.CreateDatabaseConnect("stat")

	if err != nil || errCreate != nil {
		fmt.Println(err, errCreate)
	}

	consumeLikes := kafka.NewKafkaConsumer([]string{"127.0.0.1:29092"}, "likes", likesDb)
	consumeViews := kafka.NewKafkaConsumer([]string{"127.0.0.1:29092"}, "views", viewsDb)

	a := &AppServer{
		cfg: cfg,
		server: &http.Server{
			Addr: address,
			//	Handler: initApi(cfg, kafkaProducer, logger),
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
		err := a.server.ListenAndServe()
		if err != nil {
			a.logger.Error("Failed to start HTTP server", zap.Error(err))
		}
	}()
}

func (a *AppServer) Stop(ctx context.Context) {
	a.kafkaConsumerLikes.Close()
	a.kafkaConsumerViews.Close()
	err := a.server.Shutdown(ctx)
	if err != nil {
		a.logger.Error("Error shutting down server", zap.Error(err))
	} else {
		a.logger.Info("Server shutdown successfully")
	}
}
