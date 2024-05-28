package kafka

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"stat_service/internal/model"
	"time"

	"github.com/segmentio/kafka-go"
)

type KafkaConsumer struct {
	reader   *kafka.Reader
	database *sql.DB
}

func NewKafkaConsumer(brokers []string, topic string, db *sql.DB) *KafkaConsumer {
	return &KafkaConsumer{
		reader: kafka.NewReader(kafka.ReaderConfig{
			Brokers: brokers,
			Topic:   topic,
		}),
		database: db,
	}
}

func (k *KafkaConsumer) ConsumeViews() {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:        []string{"socnet-kafka:9092"},
		Topic:          "views",
		SessionTimeout: time.Second * 6,
	})
	defer reader.Close()

	for {
		msg, err := reader.ReadMessage(context.Background())
		if err != nil {
			fmt.Println("Error fetching message:", err)
			continue
		}
		fmt.Println(msg.Value)
		var view model.NewView
		err = json.Unmarshal(msg.Value, &view)
		if err != nil {
			fmt.Println("Error unmarshalling trip:", err)
			continue
		}
		fmt.Println(view)
		k.writeToPostgresView(view)

		err = k.reader.CommitMessages(context.Background(), msg)
		if err != nil {
			fmt.Println("Error committing message:", err)
		}

		time.Sleep(300 * time.Millisecond)
	}
}

func (k *KafkaConsumer) ConsumeLikes() {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:        []string{"socnet-kafka:29092"},
		Topic:          "likes",
		SessionTimeout: time.Second * 6,
	})
	defer reader.Close()

	for {
		msg, err := reader.ReadMessage(context.Background())
		if err != nil {
			fmt.Println("Error fetching message:", err)
			continue
		}
		fmt.Println(msg.Value)
		var like model.NewLike
		err = json.Unmarshal(msg.Value, &like)
		if err != nil {
			fmt.Println("Error unmarshalling trip:", err)
			continue
		}
		fmt.Println(like)
		k.writeToPostgresLike(like)

		err = k.reader.CommitMessages(context.Background(), msg)
		if err != nil {
			fmt.Println("Error committing message:", err)
		}

		time.Sleep(300 * time.Millisecond)
	}
}

func (k *KafkaConsumer) Close() {
	k.reader.Close()
}

func (k *KafkaConsumer) writeToPostgresView(event model.NewView) error {
	_, err := k.database.Exec(
		fmt.Sprintf(`INSERT INTO views (post_time, user_id, post_id) VALUES ('%s', %d, %d)`, event.Time, event.UserId, event.PostId))
	return err
}

func (k *KafkaConsumer) writeToPostgresLike(event model.NewLike) error {
	_, err := k.database.Exec(
		fmt.Sprintf(`INSERT INTO likes (post_time, user_id, post_id) VALUES ('%s', %d, %d)`, event.Time, event.UserId, event.PostId))
	return err
}
