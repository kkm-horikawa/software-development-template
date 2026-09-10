package main

import (
	"context"
	"fmt"
	"net/http"
	"os"

	"example.com/worklog-cli/internal/adapter/api"
	"example.com/worklog-cli/internal/adapter/cli"
	usecasework "example.com/worklog-cli/internal/usecase/work"
)

func main() {
	gateway := api.NewActivityGateway(http.DefaultClient, apiBaseURL())
	startWork := usecasework.NewStartWork(gateway)
	entry := cli.NewEntry(os.Args[1:], os.Stdout, startWork)
	if err := entry.Run(context.Background()); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func apiBaseURL() string {
	if value := os.Getenv("WORKLOG_API_BASE_URL"); value != "" {
		return value
	}
	return "http://127.0.0.1:8000"
}
