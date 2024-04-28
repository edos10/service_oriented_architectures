package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Http   Http   `yaml:"http"`
	SemVer string `yaml:"semver"`
}

type Http struct {
	Port int `yaml:"port"`
}

func NewConfig() (*Config, error) {
	_ = os.Setenv("HTTP_PORT", "5002")
	_ = os.Setenv("SEMVER", "1.0")

	var cfg Config

	portStr := os.Getenv("HTTP_PORT")
	if portStr == "" {
		return nil, fmt.Errorf("HTTP_PORT is not set in .env")
	}

	port, err := strconv.Atoi(portStr)
	if err != nil {
		return nil, fmt.Errorf("HTTP_PORT must be a valid integer")
	}

	cfg.Http.Port = port
	cfg.SemVer = os.Getenv("SEMVER")

	return &cfg, nil
}
