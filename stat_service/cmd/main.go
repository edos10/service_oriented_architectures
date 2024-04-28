package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"stat_service/internal/app"
	"stat_service/internal/config"

	"go.uber.org/zap"
)

func initLogger() (*zap.Logger, error) {
	return zap.NewProduction()
}

func main() {
	var cfgPath string
	flag.StringVar(&cfgPath, "config", "/internal/config.yaml", "set config path")
	flag.Parse()

	cfg, err := config.NewConfig()
	if err != nil {
		fmt.Println(fmt.Errorf("fatal: init config %w", err))
		os.Exit(1)
	}

	serviceLogger, err := initLogger()
	if err != nil {
		fmt.Println("error init logger")
		os.Exit(1)
	}

	a := app.NewAppServer(cfg, serviceLogger)

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	defer func() {
		v := recover()

		if v != nil {
			ctx, _ := context.WithTimeout(ctx, 3*time.Second)
			a.Stop(ctx)
			os.Exit(1)
		}
	}()

	a.Run()

	<-ctx.Done()
	ctx, _ = context.WithTimeout(ctx, 3*time.Second)
	a.Stop(ctx)

}
