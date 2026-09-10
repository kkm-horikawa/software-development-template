package api_test

import (
	"context"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"example.com/worklog-cli/internal/adapter/api"
	"example.com/worklog-cli/internal/domain/work"
)

func TestActivityGatewayStartsActivityThroughHTTPContract(t *testing.T) {
	var receivedBody string
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		body, err := io.ReadAll(request.Body)
		if err != nil {
			http.Error(writer, err.Error(), http.StatusInternalServerError)
			return
		}
		receivedBody = string(body)
		writer.Header().Set("Content-Type", "application/json")
		writer.WriteHeader(http.StatusCreated)
		_, _ = writer.Write([]byte(`{"id":"11111111-1111-1111-1111-111111111111","title":"設計を書く","started_at":"2026-09-09T10:00:00Z"}`))
	}))
	defer server.Close()

	title, err := work.NewTitle("設計を書く")
	if err != nil {
		t.Fatal(err)
	}
	gateway := api.NewActivityGateway(server.Client(), server.URL)
	activity, err := gateway.Start(context.Background(), title)
	if err != nil {
		t.Fatal(err)
	}

	if receivedBody != `{"title":"設計を書く"}` {
		t.Fatalf("request body = %q", receivedBody)
	}
	if activity.ID() != "11111111-1111-1111-1111-111111111111" {
		t.Fatalf("activity id = %q", activity.ID())
	}
	if activity.StartedAt() != time.Date(2026, time.September, 9, 10, 0, 0, 0, time.UTC) {
		t.Fatalf("started at = %s", activity.StartedAt())
	}
}
