package repository

import (
	"context"
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"posts_service/proto"
)

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

type GrpcServer struct {
	proto.UnimplementedPostServiceServer
	Db *sql.DB
}

func (s *GrpcServer) CreatePost(ctx context.Context, req *proto.CreatePostRequest) (*proto.Post, error) {
	userID := req.UserId
	if userID <= 0 {
		return nil, status.Errorf(codes.Internal, "failed to getting id user!")
	}

	var post_id int64
	err := s.Db.QueryRowContext(ctx, `INSERT INTO posts (title, text_description, post_time, user_id) 
	                                 VALUES ($1, $2, $3, $4) RETURNING id`,
		req.Title, req.TextDescription, req.PostTime, req.UserId).Scan(&post_id)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "unable create post: %v", err)
	}

	return &proto.Post{
		Id:              post_id,
		Title:           req.Title,
		TextDescription: req.TextDescription,
		UserId:          req.UserId,
		PostTime:        req.PostTime,
	}, nil
}

func (s *GrpcServer) UpdatePost(ctx context.Context, r *proto.UpdatePostRequest) (*proto.Post, error) {

	if len(r.Title) != 0 {
		resUpd, err := s.Db.ExecContext(ctx, "UPDATE posts SET title = $1 WHERE id = $2 AND user_id = $3",
			r.Title, r.PostId, r.UserId)
		if err != nil {
			return nil, status.Errorf(codes.Internal, "error in updating title post: %v", err)
		}
		rowsAffected, err := resUpd.RowsAffected()
		if err != nil {
			return nil, status.Errorf(codes.NotFound, "errot in updating title post: %v", err)
		}

		if rowsAffected == 0 {
			return nil, status.Errorf(codes.PermissionDenied, "it's unable to update this post")
		}
	}

	if len(r.TextDescription) != 0 {
		resUpd, err := s.Db.ExecContext(ctx, `UPDATE posts SET text_description = $1 
		                                      WHERE id = $2 AND user_id = $3`,
			r.TextDescription, r.PostId, r.UserId)
		if err != nil {
			return nil, status.Errorf(codes.Internal, "error in updating content post: %v", err)
		}
		rowsAffected, err := resUpd.RowsAffected()
		if err != nil {
			return nil, status.Errorf(codes.NotFound, "errot in updating content post: %v", err)
		}

		if rowsAffected == 0 {
			return nil, status.Errorf(codes.PermissionDenied, "it's unable to update this post")
		}
	}

	var post proto.Post

	errGet := s.Db.QueryRowContext(ctx, `SELECT id, title, text_description, post_time, user_id FROM posts WHERE id = $1`, r.PostId).Scan(
		&post.Id, &post.Title, &post.TextDescription, &post.PostTime, &post.UserId)

	if errGet != nil {
		return nil, status.Errorf(codes.Internal, "error in returning post: %v", errGet)
	}

	return &post, nil
}

func (s *GrpcServer) DeletePost(ctx context.Context, req *proto.DeletePostRequest) (*proto.DeletePostResponse, error) {
	resExists, errEx := s.Db.ExecContext(ctx, `SELECT * FROM posts WHERE id = $1 AND user_id = $2`,
		req.PostId, req.UserId)
	if errEx != nil {
		return nil, status.Errorf(codes.NotFound, "unable find post: %v", errEx)
	}

	rowsAffected, err := resExists.RowsAffected()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "errot in selecting post: %v", err)
	}

	if rowsAffected == 0 {
		return nil, status.Errorf(codes.PermissionDenied, "it's unable to update this post")
	}

	_, errDel := s.Db.ExecContext(ctx, `DELETE FROM posts WHERE id = $1 AND user_id = $2`,
		req.PostId, req.UserId)
	if errDel != nil {
		return nil, status.Errorf(codes.NotFound, "unable delete post: %v", errDel)
	}

	retStruct := proto.DeletePostResponse{
		IsDelete: true,
	}

	return &retStruct, nil
}

func (s *GrpcServer) GetPostOnId(ctx context.Context, req *proto.GetPostOnIdRequest) (*proto.Post, error) {
	postId := req.PostId
	if postId <= 0 {
		return nil, status.Errorf(codes.Internal, "failed to getting id post!")
	}

	var post proto.Post
	err := s.Db.QueryRowContext(ctx, "SELECT id, title, text_description, post_time, user_id FROM posts WHERE id = $1", postId).Scan(
		&post.Id, &post.Title, &post.TextDescription, &post.PostTime, &post.UserId)
	if err != nil {
		return nil, status.Errorf(codes.NotFound, "post not found")
	}

	return &post, nil
}

func (s *GrpcServer) GetPostsOnPagination(ctx context.Context, r *proto.GetPostPageRequest) (*proto.GetPostPageResponse, error) {
	rows, err := s.Db.QueryContext(ctx, "SELECT id, title, text_description, user_id, post_time FROM posts LIMIT $1 OFFSET $2",
		r.CountOnPage, (r.NumPage-1)*r.CountOnPage)

	if err != nil {
		return nil, status.Errorf(codes.Internal, "error in getting posts from db: %v", err)
	}

	defer rows.Close()

	var posts []*proto.Post
	for rows.Next() {
		var post proto.Post
		if err := rows.Scan(&post.Id, &post.Title, &post.TextDescription, &post.UserId, &post.PostTime); err != nil {
			return nil, status.Errorf(codes.Internal, "error in scan post: %v", err)
		}
		posts = append(posts, &post)
	}

	if err := rows.Err(); err != nil {
		return nil, status.Errorf(codes.Internal, "error in preprocessing rows: %v", err)
	}

	return &proto.GetPostPageResponse{
		Posts: posts,
	}, nil
}
