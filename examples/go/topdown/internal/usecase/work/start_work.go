package work

import (
	"context"
	"time"

	domainwork "example.com/topdown/internal/domain/work"
)

type ActivityRepository interface {
	Save(context.Context, domainwork.Activity) error
}

type StartWork struct {
	repository ActivityRepository
	now        func() time.Time
}

func NewStartWork(repository ActivityRepository, now func() time.Time) *StartWork {
	return &StartWork{repository: repository, now: now}
}

func (s *StartWork) Run(ctx context.Context, rawTitle string) (domainwork.Activity, error) {
	title, err := s.makeTitle(rawTitle)
	if err != nil {
		return domainwork.Activity{}, err
	}
	activity := s.startActivity(title)
	if err := s.saveActivity(ctx, activity); err != nil {
		return domainwork.Activity{}, err
	}
	return activity, nil
}

func (s *StartWork) makeTitle(raw string) (domainwork.Title, error) {
	return domainwork.NewTitle(raw)
}

func (s *StartWork) startActivity(title domainwork.Title) domainwork.Activity {
	return domainwork.Start(title, s.now())
}

func (s *StartWork) saveActivity(ctx context.Context, activity domainwork.Activity) error {
	return s.repository.Save(ctx, activity)
}
