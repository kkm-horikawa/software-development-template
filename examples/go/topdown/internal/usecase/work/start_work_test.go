package work_test

import (
	"context"
	"testing"
	"time"

	"example.com/topdown/internal/adapter/repository/memory"
	usecasework "example.com/topdown/internal/usecase/work"
)

func TestIT002_StartWorkSavesStartedActivity(t *testing.T) {
	repository := &memory.Activities{}
	startedAt := time.Date(2026, time.September, 9, 10, 0, 0, 0, time.UTC)
	startWork := usecasework.NewStartWork(repository, func() time.Time { return startedAt })

	activity, err := startWork.Run(context.Background(), "設計を書く")
	if err != nil {
		t.Fatal(err)
	}
	if activity.Title().String() != "設計を書く" || !activity.StartedAt().Equal(startedAt) {
		t.Fatalf("activity = %#v", activity)
	}
	if len(repository.All()) != 1 {
		t.Fatalf("saved activities = %d", len(repository.All()))
	}
}
