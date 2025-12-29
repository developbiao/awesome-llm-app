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
	"learn.example.agent/adk/intro/workflow/loop/subagents"
)

func init() {
	// Load environment variables from .env file.
	// We try to load it from the `go-agent` directory assuming you run from the project root,
	// then fall back to the current directory.
	//
	// Also, make sure you have copied `go-agent/.example.env` to `go-agent/.env`.
	err := godotenv.Load("go-agent/.env")
	if err != nil {
		// fallback to current directory
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

	agent, err := adk.NewLoopAgent(ctx, &adk.LoopAgentConfig{
		Name:          "reflection_aget",
		Description:   "Reflection agent with main and critique agent for iterrative task solving.",
		SubAgents:     []adk.Agent{subagents.NewMainAgent(), subagents.NewCritiqueAgent()},
		MaxIterations: 5,
	})
	if err != nil {
		log.Fatal(err)
	}

	// query := "Briefly introduce what a a multimodal embedding model is."
	query := "在中国有哪些推荐适合长期持有的指数基金? 适合持有5～10年以上的价值指数基金。"
	ctx, endSpanFn := startSpanFn(ctx, "ReflectionAgents", query)

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
	time.Sleep(20 * time.Second)
}
