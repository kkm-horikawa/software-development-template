package api

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"example.com/worklog-cli/internal/domain/work"
)

type HTTPClient interface {
	Do(*http.Request) (*http.Response, error)
}

type ActivityGateway struct {
	client  HTTPClient
	baseURL string
}

func NewActivityGateway(client HTTPClient, baseURL string) *ActivityGateway {
	return &ActivityGateway{client: client, baseURL: strings.TrimRight(baseURL, "/")}
}

func (g *ActivityGateway) Start(
	ctx context.Context, title work.Title,
) (work.Activity, error) {
	request, err := g.makeStartRequest(ctx, title)
	if err != nil {
		return work.Activity{}, err
	}
	response, err := g.sendStartRequest(request)
	if err != nil {
		return work.Activity{}, err
	}
	return g.readStartedActivity(response)
}

func (g *ActivityGateway) makeStartRequest(
	ctx context.Context, title work.Title,
) (*http.Request, error) {
	body, err := json.Marshal(map[string]string{"title": title.String()})
	if err != nil {
		return nil, fmt.Errorf("作業開始の要求を作れません: %w", err)
	}
	request, err := http.NewRequestWithContext(
		ctx, http.MethodPost, g.baseURL+"/activities", bytes.NewReader(body),
	)
	if err != nil {
		return nil, fmt.Errorf("作業開始の要求を作れません: %w", err)
	}
	request.Header.Set("Content-Type", "application/json")
	return request, nil
}

func (g *ActivityGateway) sendStartRequest(request *http.Request) (*http.Response, error) {
	response, err := g.client.Do(request)
	if err != nil {
		return nil, fmt.Errorf("作業開始の結果を確認できません: バックエンドへ作業開始を依頼できません: %w", err)
	}
	return response, nil
}

func (g *ActivityGateway) readStartedActivity(response *http.Response) (work.Activity, error) {
	defer response.Body.Close()
	if response.StatusCode != http.StatusCreated {
		var failure struct {
			Detail string `json:"detail"`
		}
		if err := json.NewDecoder(response.Body).Decode(&failure); err == nil && failure.Detail != "" {
			return work.Activity{}, fmt.Errorf("作業開始の結果を確認できません: HTTP %d: %s", response.StatusCode, failure.Detail)
		}
		return work.Activity{}, fmt.Errorf("作業開始の結果を確認できません: HTTP %d", response.StatusCode)
	}
	var payload struct {
		ID        string    `json:"id"`
		Title     string    `json:"title"`
		StartedAt time.Time `json:"started_at"`
	}
	if err := json.NewDecoder(response.Body).Decode(&payload); err != nil {
		return work.Activity{}, fmt.Errorf("作業開始の結果を確認できません: 応答を読めません: %w", err)
	}
	title, err := work.NewTitle(payload.Title)
	if err != nil {
		return work.Activity{}, fmt.Errorf("作業開始の結果を確認できません: 応答が不正です: %w", err)
	}
	if !g.validActivityID(payload.ID) || payload.StartedAt.IsZero() {
		return work.Activity{}, fmt.Errorf("作業開始の結果を確認できません: 応答の識別子または開始時刻が不正です")
	}
	return work.RestoreActivity(payload.ID, title, payload.StartedAt), nil
}

func (g *ActivityGateway) validActivityID(value string) bool {
	if len(value) != 36 {
		return false
	}
	for index, char := range value {
		if index == 8 || index == 13 || index == 18 || index == 23 {
			if char != '-' {
				return false
			}
			continue
		}
		if !((char >= '0' && char <= '9') || (char >= 'a' && char <= 'f') || (char >= 'A' && char <= 'F')) {
			return false
		}
	}
	return true
}
