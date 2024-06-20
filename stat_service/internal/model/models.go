package model

type NewLike struct {
	Time   string `json:"time"`
	UserId int64  `json:"user_id"`
	PostId int64  `json:"post_id"`
	Author int64  `json:"author"`
}

type NewView struct {
	Time   string `json:"time"`
	UserId int64  `json:"user_id"`
	PostId int64  `json:"post_id"`
	Author int64  `json:"author"`
}
