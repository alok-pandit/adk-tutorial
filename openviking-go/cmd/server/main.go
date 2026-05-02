package main

import (
	"fmt"
	"log"
	"net/http"

	"openviking-go/internal/config"
	"github.com/valyala/fasthttp"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatal("Failed to load config:", err)
	}

	fmt.Printf("OpenViking Go Server starting...\n")
	fmt.Printf("Workspace: %s\n", cfg.Storage.Workspace)
	fmt.Printf("VLM Model: %s (%s)\n", cfg.VLM.Model, cfg.VLM.Provider)
	fmt.Printf("Embedding Model: %s (%s)\n", cfg.Embedding.Dense.Model, cfg.Embedding.Dense.Provider)

	// Health check
	fasthttp.ListenAndServe(":1933", func(ctx *fasthttp.RequestCtx) {
		switch string(ctx.Path()) {
		case "/health":
			ctx.SetStatusCode(200)
			ctx.SetBody([]byte(`{"status": "healthy"}`))
		case "/status":
			resp := fmt.Sprintf(`{"status": "running", "workspace": "%s", "vlm_model": "%s"}`, cfg.Storage.Workspace, cfg.VLM.Model)
			ctx.SetStatusCode(200)
			ctx.SetBodyString(resp)
		default:
			ctx.Error("Not found", http.StatusNotFound)
		}
	})

	fmt.Println("Server stopped")
}

