# OpenViking Go Clone

Go implementation of OpenViking context database for AI agents, interoperable with ADK Python/Go, LangGraph.

## Quick Start

1. `cd openviking-go && go mod tidy`
2. Copy `config/ov.conf.example` to `~/.openviking-go/ov.conf` and configure models.
3. `go run cmd/server/main.go` (starts on :1933)
4. `go install cmd/ov@latest` then `ov status`

## Config (ov.conf)

```json
{
  "storage": {"workspace": "./workspace"},
  "vlm": {"provider": "litellm", "model": "gpt-4o-mini", "api_key": "..."},
  "embedding": {"provider": "litellm", "model": "text-embedding-3-small", "dimension": 1536, "api_key": "..."}
}
```

See full docs in original OpenViking README.

