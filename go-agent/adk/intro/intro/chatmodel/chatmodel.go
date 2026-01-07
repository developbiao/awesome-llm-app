package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"os"

	"github.com/cloudwego/eino/adk"
	"github.com/cloudwego/eino/components/tool"
	"learn.example.agent/adk/common/prints"
	"learn.example.agent/adk/common/store"
	"learn.example.agent/adk/intro/intro/chatmodel/subagents"
)

func main() {
	ctx := context.Background()
	agent := subagents.NewBookRecommendAgent()
	runner := adk.NewRunner(ctx, adk.RunnerConfig{
		EnableStreaming: true,
		Agent:           agent,
		CheckPointStore: store.NewInMemoryStore(),
	})
	iter := runner.Query(ctx, "recommend a book to me", adk.WithCheckPointID("1"))
	for {
		event, ok := iter.Next()
		if !ok {
			break
		}
		if event.Err != nil {
			log.Fatal(event.Err)
		}
		prints.Event(event)
	}

	scanner := bufio.NewScanner(os.Stdin)
	fmt.Print("\nyour input here:")
	scanner.Scan()
	fmt.Println()
	nInput := scanner.Text()

	iter, err := runner.Resume(ctx, "1", adk.WithToolOptions([]tool.Option{subagents.WithNewInput(nInput)}))
	if err != nil {
		log.Fatal(err)
	}
	for {
		event, ok := iter.Next()
		if !ok {
			break
		}
		if event.Err != nil {
			log.Fatal(event.Err)
		}
		prints.Event(event)
	}
}
