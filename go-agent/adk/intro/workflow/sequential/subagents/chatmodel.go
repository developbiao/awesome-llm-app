package subagents

import (
	"context"
	"log"

	"github.com/cloudwego/eino-examples/adk/common/model"
	"github.com/cloudwego/eino/adk"
)

// NewPlanAgent creates a new agent for generating a research plan.
func NewPlanAgent() adk.Agent {
	agent, err := adk.NewChatModelAgent(context.Background(), &adk.ChatModelAgentConfig{
		Name:        "PlannerAgent",
		Description: "Generates a research plan based on a topic.",
		Instruction: `
You are an expert research planner.
Your goal is to create a comprehensive, step-by-step research plan for a given topic.
The plan should be logical, clear, and easy to follow.
The user will provide the research topic. Your output must ONLY be the research plan itself. without any converesational text,  introductions, or summaries.`,
		Model:     model.NewChatModel(),
		OutputKey: "Plan",
	})
	if err != nil {
		log.Fatal(err)
	}
	return agent
}

// NewWriterAgent creates a new agent for writing a report based on a research plan.
func NewWriterAgent() adk.Agent {
	agent, err := adk.NewChatModelAgent(context.Background(), &adk.ChatModelAgentConfig{
		Name:        "WriterAgent",
		Description: "Writes a report based on a research plan.",
		Instruction: `
You are an expiret academic writer.
You will be provided with a detailed research plan:
{Plan}

Your task is to expand on this plan to write a comprehensive, well-structured, and in-depth report.`,
		Model: model.NewChatModel(),
	})

	if err != nil {
		log.Fatal(err)
	}
	return agent
}
