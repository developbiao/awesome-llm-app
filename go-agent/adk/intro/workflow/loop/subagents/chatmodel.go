package subagents

import (
	"context"
	"log"

	"github.com/cloudwego/eino-examples/adk/common/model"
	"github.com/cloudwego/eino/adk"
	"github.com/cloudwego/eino/components/tool"
	"github.com/cloudwego/eino/components/tool/utils"
	"github.com/cloudwego/eino/compose"
)

// NewMainAgent creates a new main agent.
func NewMainAgent() adk.Agent {
	agent, err := adk.NewChatModelAgent(context.Background(), &adk.ChatModelAgentConfig{
		Name:        "main_agent",
		Description: "Main agent that attempts to solve the user's task",
		Instruction: `You are the main agent repsonsible for solviing the user's task.
Provider a comprehensive solution based on the given requirements.
Focus on delivering accurate and complete results.
		`,
		Model: model.NewChatModel(),
	})

	if err != nil {
		log.Fatal(err)
	}
	return agent
}

// NewCritiqueAgent creates a new critique agent.
func NewCritiqueAgent() adk.Agent {
	exitAndSummarizeTool, err := utils.InferTool("exit_and_summarize", "exit from the loop and provide a final summary response",
		func(ctx context.Context, req *exitAndSummarize) (string, error) {
			_ = adk.SendToolGenAction(ctx, "exit_and_summarize", adk.NewBreakLoopAction("critique_agent"))
			return req.Summary, nil
		})
	if err != nil {
		log.Fatalf("create tool failed, name=%v, err=%v", "exit_and_summarize", err)
	}
	agent, err := adk.NewChatModelAgent(context.Background(), &adk.ChatModelAgentConfig{
		Name:        "critique_agent",
		Description: "Critique agent that reviews the main agent's work and provides feedback.",
		Instruction: `You are a critique agent responsible for reviewing the main agent's work.
Analyze the provided solution for accuracy, completeness, and quality.
If you find issues or areas for improvement, provide specific feedback.
If the work is satisfactory, call the 'exit_and_summarize' tool and provide a final summary response.`,
		Model: model.NewChatModel(),
		ToolsConfig: adk.ToolsConfig{
			ToolsNodeConfig: compose.ToolsNodeConfig{
				Tools: []tool.BaseTool{
					exitAndSummarizeTool,
				},
			},
			ReturnDirectly: map[string]bool{
				"exit_and_summarize": true,
			},
		},
	})
	if err != nil {
		log.Fatalf("create agent failed, name=%v, err=%v", "critique_agent", err)
	}
	return agent
}

type exitAndSummarize struct {
	Summary string `json:"summary" jsonschema_description:"final summary of the solution"`
}
