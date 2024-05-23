package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"posts_service/internal/app"

	"go.uber.org/zap"
)

func initLogger() (*zap.Logger, error) {
	return zap.NewProduction()
}

func main() {
	serviceLogger, err := initLogger()
	if err != nil {
		fmt.Println("error init logger")
		os.Exit(1)
	}

	a := app.NewAppServer(serviceLogger)

	_, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	defer func() {
		v := recover()

		if v != nil {
			os.Exit(1)
		}
	}()

	a.Run()

}
