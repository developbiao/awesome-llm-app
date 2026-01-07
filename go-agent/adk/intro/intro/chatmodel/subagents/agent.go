package subagents

import (
	"context"
	"fmt"
	"log"

	"github.com/cloudwego/eino-examples/adk/common/model"
	"github.com/cloudwego/eino/adk"
	"github.com/cloudwego/eino/components/tool"
	"github.com/cloudwego/eino/compose"
)

// NewBookRecommendAgent creates a new book recommendation agent.
func NewBookRecommendAgent() adk.Agent {
	ctx := context.Background()

	agent, err := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
		Name:        "Book Recommender",
		Description: "An agent that can recommend books",
		Instruction: `You are an expert book recommender.
Based on the user's request, use the "search_book" tool to find relevant books, Finally, present the results to the user.`,
		Model: model.NewChatModel(),
		ToolsConfig: adk.ToolsConfig{
			ToolsNodeConfig: compose.ToolsNodeConfig{
				Tools: []tool.BaseTool{NewBookRecommender(), NewAskForClarificationTool()},
			},
		},
	})

	if err != nil {
		log.Fatal(fmt.Errorf("failed to create chatmodel: %w", err))
	}
	return agent
}
