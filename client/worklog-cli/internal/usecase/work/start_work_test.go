package work_test

import (
	"context"
	"testing"
	"time"

	"example.com/worklog-cli/internal/domain/work"
	usecasework "example.com/worklog-cli/internal/usecase/work"
)

func TestIT_1_02_StartWorkRequestsStartedActivity(t *testing.T) {
	startedAt := time.Date(2026, time.September, 9, 10, 0, 0, 0, time.UTC)
	title, err := work.NewTitle("設計を書く")
	if err != nil {
		t.Fatal(err)
	}
	gateway := &activityGatewayStub{activity: work.RestoreActivity(
		"11111111-1111-1111-1111-111111111111", title, startedAt,
	)}
	startWork := usecasework.NewStartWork(gateway)

	activity, err := startWork.Run(context.Background(), "設計を書く")
	if err != nil {
		t.Fatal(err)
	}
	if activity.Title().String() != "設計を書く" || !activity.StartedAt().Equal(startedAt) {
		t.Fatalf("activity = %#v", activity)
	}
	if gateway.receivedTitle.String() != "設計を書く" {
		t.Fatalf("received title = %q", gateway.receivedTitle.String())
	}
}

type activityGatewayStub struct {
	activity      work.Activity
	receivedTitle work.Title
}

func (g *activityGatewayStub) Start(_ context.Context, title work.Title) (work.Activity, error) {
	g.receivedTitle = title
	return g.activity, nil
}
