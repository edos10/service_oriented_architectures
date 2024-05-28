package repository

import (
	"context"
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"stat_service/proto"
)

type GrpcServer struct {
	proto.UnimplementedStatServiceServer
	Db *sql.DB
}

func CreateDatabaseConnect(dbname string) (*sql.DB, error) {
	dbHost := "postgresql"   //os.Getenv("DB_HOST")
	dbPort := "5432"         //os.Getenv("DB_PORT")
	dbUser := "postgres"     //os.Getenv("DB_USER_NAME")
	dbPassword := "postgres" //os.Getenv("DB_PASSWORD")
	dbName := dbname         //os.Getenv("DB_NAME")
	//connectionString := fmt.Sprintf("postgres://%v:%v@%v:%v/%v?sslmode=disable",
	//	dbUser, dbPassword, dbHost, dbPort, dbName)
	dataSourceName := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName)
	//fmt.Println(connectionString)
	db, err := sql.Open("postgres", dataSourceName)
	return db, err
}

func (s *GrpcServer) GetStatPost(ctx context.Context, req *proto.GetStatPostRequest) (*proto.StatPostResponse, error) {
	var likes, views int64

	postId := req.PostId

	err := s.Db.QueryRowContext(ctx, "SELECT COUNT(*) FROM likes WHERE post_id = $1", postId).Scan(&likes)
	if err != nil {
		log.Printf("Error fetching likes count for post: %v", err)
		return nil, status.Errorf(codes.Internal, "Error fetching likes count for post")
	}

	err = s.Db.QueryRowContext(ctx, "SELECT COUNT(*) FROM views WHERE post_id = $1", req.PostId).Scan(&views)
	if err != nil {
		log.Printf("Error fetching views count for post: %v", err)
		return nil, status.Errorf(codes.Internal, "Error fetching views count for post")
	}

	return &proto.StatPostResponse{PostId: postId, Likes: likes, Views: views}, nil
}
