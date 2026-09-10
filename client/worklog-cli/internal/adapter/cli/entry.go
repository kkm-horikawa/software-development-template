package cli

import (
	"context"
	"errors"
	"fmt"
	"io"

	domainwork "example.com/worklog-cli/internal/domain/work"
	usecasework "example.com/worklog-cli/internal/usecase/work"
)

var ErrUsage = errors.New("使い方: worklog start <作業名>")

type Entry struct {
	args      []string
	out       io.Writer
	startWork *usecasework.StartWork
}

func NewEntry(args []string, out io.Writer, startWork *usecasework.StartWork) *Entry {
	return &Entry{args: args, out: out, startWork: startWork}
}

func (e *Entry) Run(ctx context.Context) error {
	title, err := e.readStartCommand()
	if err != nil {
		return err
	}
	activity, err := e.startActivity(ctx, title)
	if err != nil {
		return err
	}
	return e.writeActivity(activity)
}

func (e *Entry) readStartCommand() (string, error) {
	if len(e.args) != 2 || e.args[0] != "start" {
		return "", ErrUsage
	}
	return e.args[1], nil
}

func (e *Entry) startActivity(ctx context.Context, title string) (domainwork.Activity, error) {
	return e.startWork.Run(ctx, title)
}

func (e *Entry) writeActivity(activity domainwork.Activity) error {
	_, err := fmt.Fprintf(e.out, "開始: %s\n", activity.Title().String())
	return err
}
