package work

import (
	"errors"
	"strings"
	"time"
)

var ErrEmptyTitle = errors.New("作業名を空にはできません")

type Title struct {
	value string
}

func NewTitle(raw string) (Title, error) {
	value := strings.TrimSpace(raw)
	if value == "" {
		return Title{}, ErrEmptyTitle
	}
	return Title{value: value}, nil
}

func (t Title) String() string {
	return t.value
}

type Activity struct {
	title     Title
	startedAt time.Time
}

func Start(title Title, startedAt time.Time) Activity {
	return Activity{title: title, startedAt: startedAt}
}

func (a Activity) Title() Title {
	return a.title
}

func (a Activity) StartedAt() time.Time {
	return a.startedAt
}
