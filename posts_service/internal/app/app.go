package app

import (
	"log"
	"net"
	"posts_service/internal/repository"
	"posts_service/proto"

	"go.uber.org/zap"
	"google.golang.org/grpc"
)

type AppServer struct {
	server *repository.GrpcServer
	logger *zap.Logger
}

func NewAppServer(logger *zap.Logger) *AppServer {
	db, err := repository.CreateDatabaseConnect("posts")
	if err != nil {
		panic("unable to connect with db...")
	}
	a := &AppServer{
		server: &repository.GrpcServer{
			Db: db,
		},
		logger: logger,
	}

	return a
}

func (a *AppServer) Run() {
	s := grpc.NewServer()
	proto.RegisterPostServiceServer(s, a.server)
	port, err := net.Listen("tcp", ":80")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	err = s.Serve(port)
	if err != nil {
		a.logger.Error("Failed to start grpc server", zap.Error(err))
	}
}
