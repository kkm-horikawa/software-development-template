package memory

import (
	"context"
	"sync"

	"example.com/topdown/internal/domain/work"
)

type Activities struct {
	mu    sync.Mutex
	items []work.Activity
}

func (a *Activities) Save(_ context.Context, activity work.Activity) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.items = append(a.items, activity)
	return nil
}

func (a *Activities) All() []work.Activity {
	a.mu.Lock()
	defer a.mu.Unlock()
	return append([]work.Activity(nil), a.items...)
}
