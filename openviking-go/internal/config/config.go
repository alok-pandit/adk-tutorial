package config

import (
	"os"

	"github.com/spf13/viper"
	"github.com/tidwall/gjson"
)

type Config struct {
	Storage struct {
		Workspace string `mapstructure:"workspace"`
	} `mapstructure:"storage"`
	Log struct {
		Level  string `mapstructure:"level"`
		Output string `mapstructure:"output"`
	} `mapstructure:"log"`
	Embedding struct {
		Dense struct {
			APIKey     string `mapstructure:"api_key"`
			APIKeyEnv  string `mapstructure:"api_key_env"`
			Provider   string `mapstructure:"provider"`
			Model      string `mapstructure:"model"`
			Dimension  int    `mapstructure:"dimension"`
			APIBase    string `mapstructure:"api_base"`
		} `mapstructure:"dense"`
		MaxConcurrent int `mapstructure:"max_concurrent"`
	} `mapstructure:"embedding"`
	VLM struct {
		APIKey        string `mapstructure:"api_key"`
		APIKeyEnv     string `mapstructure:"api_key_env"`
		Provider      string `mapstructure:"provider"`
		Model         string `mapstructure:"model"`
		APIBase       string `mapstructure:"api_base"`
		MaxConcurrent int    `mapstructure:"max_concurrent"`
	} `mapstructure:"vlm"`
}

func Load() (*Config, error) {
	configFile := os.Getenv("OPENVIKING_CONFIG_FILE")
	if configFile == "" {
		homeDir, _ := os.UserHomeDir()
		configFile = homeDir + "/.openviking-go/ov.conf"
	}

	viper.SetConfigFile(configFile)
	viper.SetConfigType("json")
	if err := viper.ReadInConfig(); err != nil {
		return nil, err
	}

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, err
	}

	// Resolve API keys from env if set
	if cfg.Embedding.Dense.APIKeyEnv != "" {
		cfg.Embedding.Dense.APIKey = os.Getenv(cfg.Embedding.Dense.APIKeyEnv)
	}
	if cfg.VLM.APIKeyEnv != "" {
		cfg.VLM.APIKey = os.Getenv(cfg.VLM.APIKeyEnv)
	}

	return &cfg, nil
}

