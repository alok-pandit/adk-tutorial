# OpenViking Go Clone - TODO

## Phase 1: Core Server + CLI + Python MCP (MVP)
- [ ] Step 1: Create project dir structure `openviking-go/` and `go.mod`
- [ ] Step 2: Implement config loading (ov.conf JSON)
- [ ] Step 3: Basic HTTP server with /health, /status endpoints
- [ ] Step 4: Virtual FS basics (in-memory dirs/files, viking:// parser)
- [ ] Step 5: CLI `ov` with cobra (status, ls)
- [ ] Step 6: Model clients (litellm/openai for embedding/VLM)
- [ ] Step 7: Python MCP SDK/tool for ADK integration
- [ ] Step 8: Test server + CLI locally

## Phase 2: Advanced Features
- [ ] Tiered context L0/L1/L2 (VLM summarization)
- [ ] Recursive retrieval with vector search (use LanceDB Go or similar)
- [ ] Auto session memory extraction

## Phase 3: Interoperability
- [ ] ADK Go SDK stub
- [ ] LangGraph Python tool
- [ ] Integration into existing ADK agents (e.g., add tool to adaptive_card_agent)
- [ ] Docker deployment
- [ ] Full E2E tests

**Current Progress: Steps 1-5 complete (go.mod, config, basic server, CLI status). Proceeding to Step 6 (model clients). Workspace ready for testing.**&#10;&#10;Next: Test with `go run cmd/server/main.go` (expect /status on :1933) and `go run cmd/ov/main.go status`

