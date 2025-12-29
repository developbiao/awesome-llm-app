package main

import (
	"context"
	"fmt"
	"log"

	"learn.example.agent/adk/common/prints"
	"learn.example.agent/adk/common/trace"

	"github.com/cloudwego/eino/adk"
	"learn.example.agent/adk/intro/workflow/sequential/subagents"
)

func main() {
	ctx := context.Background()

	traceCloseFn, startSpanFn := trace.AppendCozeLoopCallbackIfConfigured(ctx)
	defer traceCloseFn(ctx)

	agent, err := adk.NewSequentialAgent(ctx, &adk.SequentialAgentConfig{
		Name:        "ResearchAgent",
		Description: "A sequential workflow fow planning and writing a research report.",
		SubAgents: []adk.Agent{
			subagents.NewPlanAgent(),
			subagents.NewWriterAgent(),
		},
	})
	if err != nil {
		log.Fatal(err)
	}

	query := "成都青城山与都江堰的人文历史故事"
	ctx, endSpanFn := startSpanFn(ctx, "layered-supervisor", query)

	runner := adk.NewRunner(ctx, adk.RunnerConfig{
		EnableStreaming: true, // you can disable streaming here
		Agent:           agent,
	})

	var lastMessage adk.Message

	iter := runner.Query(ctx, query)
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
