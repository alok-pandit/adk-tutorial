package main

import (
	"fmt"
	"log"
	"os/exec"

	"openviking-go/internal/config"
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "ov",
	Short: "OpenViking Go CLI",
}

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show server status",
	Run: func(cmd *cobra.Command, args []string) {
		cfg, err := config.Load()
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("Workspace: %s\n", cfg.Storage.Workspace)
		fmt.Printf("VLM: %s (%s)\n", cfg.VLM.Model, cfg.VLM.Provider)
		fmt.Printf("Embedding: %s dim=%d (%s)\n", cfg.Embedding.Dense.Model, cfg.Embedding.Dense.Dimension, cfg.Embedding.Dense.Provider)
	},
}

func main() {
	rootCmd.AddCommand(statusCmd)
	if err := rootCmd.Execute(); err != nil {
		log.Fatal(err)
	}
}

