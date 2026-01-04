package main

import (
	"context"
	"log"

	"github.com/cloudwego/eino-ext/components/model/ollama"
	"github.com/cloudwego/eino/components/model"
)

func createOllamaChatModel(ctx context.Context) model.ToolCallingChatModel {
	chatModel, err := ollama.NewChatModel(ctx, &ollama.ChatModelConfig{
		BaseURL: "http://localhost:11434",
		Model:   "llama2",
	})
	if err != nil {
		log.Fatalf("create ollama chat model failed, err=%v", err)
	}
	return chatModel
}
