package review

import (
	"context"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

const timeout = time.Second * 3

// Queue implements a news story review queue based on redis.
type Queue struct {
	client  *redis.Client
	channel string
}

// NewQueue initializes a new queue using the specified redis instance address.
// Messages will be published on the specified channel.
func NewQueue(addr string, channel string) *Queue {
	rd := redis.NewClient(&redis.Options{
		Addr: addr,
	})

	return &Queue{
		client:  rd,
		channel: channel,
	}
}

// EnqueueReview pushes a new news story to be reviewed into the queue.
func (q *Queue) EnqueueReview(ctx context.Context, storyID string) error {
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	_, err := q.client.Publish(ctx, q.channel, storyID).Result()
	if err != nil {
		return fmt.Errorf("publishing message to redis: %w", err)
	}

	return nil
}
