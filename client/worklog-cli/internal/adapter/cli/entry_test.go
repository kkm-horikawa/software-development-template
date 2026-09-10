package cli_test

import (
	"bytes"
	"context"
	"testing"
	"time"

	"example.com/worklog-cli/internal/adapter/cli"
	"example.com/worklog-cli/internal/domain/work"
	usecasework "example.com/worklog-cli/internal/usecase/work"
)

func TestST002_EntryStartsWorkFromCommand(t *testing.T) {
	gateway := &activityGatewayStub{activity: work.RestoreActivity(
		"11111111-1111-1111-1111-111111111111",
		mustTitle(t, "設計を書く"),
		time.Date(2026, time.September, 9, 10, 0, 0, 0, time.UTC),
	)}
	startWork := usecasework.NewStartWork(gateway)
	var output bytes.Buffer
	entry := cli.NewEntry([]string{"start", "設計を書く"}, &output, startWork)

	if err := entry.Run(context.Background()); err != nil {
		t.Fatal(err)
	}
	if output.String() != "開始: 設計を書く\n" {
		t.Fatalf("output = %q", output.String())
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

func mustTitle(t *testing.T, raw string) work.Title {
	t.Helper()
	title, err := work.NewTitle(raw)
	if err != nil {
		t.Fatal(err)
	}
	return title
}
