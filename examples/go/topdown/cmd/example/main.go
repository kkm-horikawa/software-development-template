package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"example.com/topdown/internal/adapter/cli"
	"example.com/topdown/internal/adapter/repository/memory"
	usecasework "example.com/topdown/internal/usecase/work"
)

func main() {
	repository := &memory.Activities{}
	startWork := usecasework.NewStartWork(repository, time.Now)
	entry := cli.NewEntry(os.Args[1:], os.Stdout, startWork)
	if err := entry.Run(context.Background()); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
