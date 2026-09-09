package work

import (
	"context"

	domainwork "example.com/worklog-cli/internal/domain/work"
)

type ActivityGateway interface {
	Start(context.Context, domainwork.Title) (domainwork.Activity, error)
}

type StartWork struct {
	gateway ActivityGateway
}

func NewStartWork(gateway ActivityGateway) *StartWork {
	return &StartWork{gateway: gateway}
}

func (s *StartWork) Run(ctx context.Context, rawTitle string) (domainwork.Activity, error) {
	title, err := s.makeTitle(rawTitle)
	if err != nil {
		return domainwork.Activity{}, err
	}
	return s.requestStart(ctx, title)
}

func (s *StartWork) makeTitle(raw string) (domainwork.Title, error) {
	return domainwork.NewTitle(raw)
}

func (s *StartWork) requestStart(
	ctx context.Context, title domainwork.Title,
) (domainwork.Activity, error) {
	return s.gateway.Start(ctx, title)
}
