package work_test

import (
	"errors"
	"testing"

	"example.com/topdown/internal/domain/work"
)

func TestNewTitleTrimsSurroundingSpaces(t *testing.T) {
	title, err := work.NewTitle("  設計を書く  ")
	if err != nil {
		t.Fatal(err)
	}
	if title.String() != "設計を書く" {
		t.Fatalf("title = %q", title.String())
	}
}

func TestNewTitleRefusesEmptyValue(t *testing.T) {
	_, err := work.NewTitle("   ")
	if !errors.Is(err, work.ErrEmptyTitle) {
		t.Fatalf("err = %v", err)
	}
}
