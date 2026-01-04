package main

import (
	"context"
	"log"
	"time"

	"github.com/cloudwego/eino/adk"
	"github.com/cloudwego/eino/adk/prebuilt/planexecute"
	"learn.example.agent/adk/common/prints"
	"learn.example.agent/adk/common/trace"
	"learn.example.agent/adk/multiagent/plan-execute-replan/agent"
)

func main() {
	ctx := context.Background()

	traceCloseFn, startSpanFn := trace.AppendCozeLoopCallbackIfConfigured(ctx)
	defer traceCloseFn(ctx)

	planAgent, err := agent.NewPlanner(ctx)
	if err != nil {
		log.Fatalf("agent.newPlanner failed, err: %v", err)
	}

	executeAgent, err := agent.NewExecutor(ctx)
	if err != nil {
		log.Fatalf("agent.NewExecutor failed, err: %v", err)
	}

	replanAgent, err := agent.NewReplanAgent(ctx)
	if err != nil {
		log.Fatalf("agent.NewReplanAgent failed, err: %v", err)
	}

	entryAgent, err := planexecute.New(ctx, &planexecute.Config{
		Planner:       planAgent,
		Executor:      executeAgent,
		Replanner:     replanAgent,
		MaxIterations: 10,
	})
	if err != nil {
		log.Fatalf("NewPlanExecuteReplan failed, err: %v", err)
	}

	r := adk.NewRunner(ctx, adk.RunnerConfig{
		Agent: entryAgent,
	})

	query := "Plan a 3-day trip to Beijing in Next Month. I need flights from ChengDu, hotel recommendations, and must-see attractions. Today is 2025-09-09"
	ctx, endSpanFn := startSpanFn(ctx, "plan-execute-replan", query)
	iter := r.Query(ctx, query)
	var lastMessage adk.Message
	for {
		event, ok := iter.Next()
		if !ok {
			break
		}

		prints.Event(event)

		if event.Output != nil {
			lastMessage, _, err = adk.GetMessage(event)
		}

		endSpanFn(ctx, lastMessage)
	}

	// wait for all span to be ended
	time.Sleep(5 * time.Second)

}
