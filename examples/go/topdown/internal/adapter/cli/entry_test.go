package cli_test

import (
	"bytes"
	"context"
	"testing"
	"time"

	"example.com/topdown/internal/adapter/cli"
	"example.com/topdown/internal/adapter/repository/memory"
	usecasework "example.com/topdown/internal/usecase/work"
)

func TestST002_EntryStartsWorkFromCommand(t *testing.T) {
	repository := &memory.Activities{}
	startWork := usecasework.NewStartWork(repository, func() time.Time {
		return time.Date(2026, time.September, 9, 10, 0, 0, 0, time.UTC)
	})
	var output bytes.Buffer
	entry := cli.NewEntry([]string{"start", "設計を書く"}, &output, startWork)

	if err := entry.Run(context.Background()); err != nil {
		t.Fatal(err)
	}
	if output.String() != "開始: 設計を書く\n" {
		t.Fatalf("output = %q", output.String())
	}
	if len(repository.All()) != 1 {
		t.Fatalf("saved activities = %d", len(repository.All()))
	}
}
