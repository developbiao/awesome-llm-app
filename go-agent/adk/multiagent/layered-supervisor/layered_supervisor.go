package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/cloudwego/eino/adk"
	"github.com/joho/godotenv"
	"learn.example.agent/adk/common/prints"
	"learn.example.agent/adk/common/trace"
)

func init() {
	err := godotenv.Load("go-agent/.env")
	if err != nil {
		err = godotenv.Load()
	}

	if err != nil {
		log.Fatalf("Error loading .env file: %v. Please ensure a .env file exists in the 'go-agent' directory or the current working directory.", err)
	}

	log.Println("Successfully loaded environment variables:")
}

func main() {
	ctx := context.Background()

	traceCloseFn, startSpanFn := trace.AppendCozeLoopCallbackIfConfigured(ctx)
	defer traceCloseFn(ctx)

	sv, err := buildSupervisor(ctx)
	if err != nil {
		log.Fatalf("Build layered supervisor failed: %v", err)
	}

	query := "find US and New York state GDP in 2024. what % of US GDP was New York state? " +
		"The multiply that precentage by 1.589. "

	ctx, endSpanFn := startSpanFn(ctx, "layered-superviosr", query)
	iter := adk.NewRunner(ctx, adk.RunnerConfig{
		EnableStreaming: true,
		Agent:           sv,
	}).Query(ctx, query)

	fmt.Println("\nuser query: ", query)

	var lastMessage adk.Message
	for {
		event, hasEvent := iter.Next()
		if !hasEvent {
			break
		}

		prints.Event(event)

		if event.Output != nil {
			lastMessage, _, err = adk.GetMessage(event)
		}
	}

	endSpanFn(ctx, lastMessage)

	// Wait for all span to be ended
	time.Sleep(5 * time.Second)
}
