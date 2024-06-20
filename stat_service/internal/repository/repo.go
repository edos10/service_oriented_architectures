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

func (s *GrpcServer) GetTopNUsers(ctx context.Context, req *proto.GetTopNUsersRequest) (*proto.GetTopNUsersResponse, error) {
	query_like := "SELECT author, COUNT(*) as total_likes FROM likes GROUP BY author ORDER BY total_likes DESC LIMIT $1"
	rows, err := s.Db.QueryContext(ctx, query_like, req.Top_N)
	if err != nil {
		log.Printf("Error fetching top N users: %v", err)
		return nil, status.Errorf(codes.Internal, "Error fetching top N users")
	}
	defer rows.Close()

	var users []*proto.TopUsersLikes
	for rows.Next() {
		var user proto.TopUsersLikes
		if err := rows.Scan(&user.UserId, &user.TotalLikes); err != nil {
			log.Printf("Error scanning user row: %v", err)
			continue
		}
		users = append(users, &user)
	}
	if err := rows.Err(); err != nil {
		log.Printf("Error iterating over user rows: %v", err)
		return nil, status.Errorf(codes.Internal, "Error iterating over user rows")
	}

	return &proto.GetTopNUsersResponse{Users: users}, nil
}


func (s *GrpcServer) GetTopPosts(ctx context.Context, req *proto.GetTopPostsRequest) (*proto.GetTopPostsResponse, error) {
	if req.Views {
		query_views := "SELECT post_id, COUNT(*) as total_views FROM views GROUP BY post_id ORDER BY total_views DESC LIMIT 5"
		rows, err := s.Db.QueryContext(ctx, query_views)
		if err != nil {
			log.Printf("Error fetching top 5 posts: %v", err)
			return nil, status.Errorf(codes.Internal, "Error fetching top 5 posts")
		}
		defer rows.Close()
		var posts []*proto.AbstractStatPost
		for rows.Next() {
			var post proto.AbstractStatPost
			if err := rows.Scan(&post.Id, &post.Amount); err != nil {
				log.Printf("Error scanning post row: %v", err)
				continue
			}
			err := s.Db.QueryRowContext(ctx, "SELECT author FROM views WHERE post_id = $1", post.Id).Scan(&post.Author)
			if err != nil {
				return nil, status.Errorf(codes.NotFound, "post not found")
			}
			posts = append(posts, &post)
		}
		if err := rows.Err(); err != nil {
			log.Printf("Error iterating over post rows: %v", err)
			return nil, status.Errorf(codes.Internal, "Error iterating over post rows")
		}
	
		return &proto.GetTopPostsResponse{Posts: posts}, nil
	}
	query_like := "SELECT post_id, COUNT(*) as total_likes FROM likes GROUP BY post_id ORDER BY total_likes DESC LIMIT 5"
	rows, err := s.Db.QueryContext(ctx, query_like)
	if err != nil {
		log.Printf("Error fetching top 5 posts: %v", err)
		return nil, status.Errorf(codes.Internal, "Error fetching top 5 posts")
	}
	defer rows.Close()
	var posts []*proto.AbstractStatPost
	for rows.Next() {
		var post proto.AbstractStatPost
		if err := rows.Scan(&post.Id, &post.Amount); err != nil {
			log.Printf("Error scanning post row: %v", err)
			continue
		}
		err := s.Db.QueryRowContext(ctx, "SELECT author FROM likes WHERE post_id = $1", post.Id).Scan(&post.Author)
		if err != nil {
			return nil, status.Errorf(codes.NotFound, "post not found")
		}
		posts = append(posts, &post)
	}
	if err := rows.Err(); err != nil {
		log.Printf("Error iterating over post rows: %v", err)
		return nil, status.Errorf(codes.Internal, "Error iterating over post rows")
	}

	return &proto.GetTopPostsResponse{Posts: posts}, nil
}
