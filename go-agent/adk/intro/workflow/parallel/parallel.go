package main

import (
	"context"
	"fmt"
	"log"

	"github.com/cloudwego/eino/adk"
	"github.com/joho/godotenv"
	"learn.example.agent/adk/common/prints"
	"learn.example.agent/adk/common/trace"
	"learn.example.agent/adk/intro/workflow/parallel/subagents"
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

	agent, err := adk.NewParallelAgent(ctx, &adk.ParallelAgentConfig{
		Name:        "DataCollecitonAgent",
		Description: "Data Collection Agent could collect data from multiple sources.",
		SubAgents: []adk.Agent{
			subagents.NewStockDataCollectionAgent(),
			subagents.NewNewsDataCollectionAgent(),
			subagents.NewSocialMediaInfoCollectionAgent(),
		},
	})
	if err != nil {
		log.Fatal(err)
	}

	query := "分析一下中国平安这支股票的发展情况与风险。"
	ctx, endSpanFn := startSpanFn(ctx, "layered-supervisor", query)

	runner := adk.NewRunner(ctx, adk.RunnerConfig{
		EnableStreaming: true,
		Agent:           agent,
	})

	iter := runner.Query(ctx, query)
	var lastMessage adk.Message

	for {
		event, ok := iter.Next()
		if !ok {
			break
		}
		if event.Err != nil {
			fmt.Printf("Error: %v\n", event.Err)
			break
		}

		prints.Event(event)
		if event.Output != nil {
			lastMessage, _, err = adk.GetMessage(event)
		}
	}

	endSpanFn(ctx, lastMessage)

}
