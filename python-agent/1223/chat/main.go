package main

import (
	"context"
	"log"
)

func main() {
	ctx := context.Background()

	// Use template create messages
	log.Printf("=== create messages ===\n")
	messages := createMessagesFromTemplate()
	log.Printf("message: %+v\n\n", messages)

	// Create llm
	log.Printf("=== Create llm ===\n")
	chatModel := createOpenAIChatModel(ctx)
	log.Printf("Create llm success\n\n")

	log.Printf("=== llm generate ===\n")
	result := generate(ctx, chatModel, messages)
	log.Printf("result: %+v\n\n", result)

	log.Printf("===llm stream generate ===\n")
	streamResult := stream(ctx, chatModel, messages)
	reportStream(streamResult)
}
