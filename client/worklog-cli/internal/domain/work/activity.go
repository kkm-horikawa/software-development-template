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
	id        string
	title     Title
	startedAt time.Time
}

func RestoreActivity(id string, title Title, startedAt time.Time) Activity {
	return Activity{id: id, title: title, startedAt: startedAt}
}

func (a Activity) ID() string {
	return a.id
}

func (a Activity) Title() Title {
	return a.title
}

func (a Activity) StartedAt() time.Time {
	return a.startedAt
}
