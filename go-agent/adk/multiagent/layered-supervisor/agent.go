package main

import (
	"context"
	"errors"
	"fmt"

	"github.com/cloudwego/eino-examples/adk/common/model"
	"github.com/cloudwego/eino-examples/flow/agent/multiagent/plan_execute/tools"
	"github.com/cloudwego/eino/adk"
	"github.com/cloudwego/eino/adk/prebuilt/supervisor"
	"github.com/cloudwego/eino/components/tool"
	"github.com/cloudwego/eino/compose"
)

// buildSearchAgent
func buildSearchAgent(ctx context.Context) (adk.Agent, error) {
	m := model.NewChatModel()

	type searchReq struct {
		Query string `json:"query"`
	}

	type searchResp struct {
		Result string `json:"result"`
	}

	search := func(ctx context.Context, req *searchReq) (*searchResp, error) {
		return &searchResp{
			Result: "In 2024, the US GDP was $23 trillion and New York State's GDP was $2.297 trillion",
		}, nil
	}

	searchTool, err := tools.SafeInferTool("search", "search the internet for info", search)
	if err != nil {
		return nil, err
	}
	return adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
		Name:        "research_agent",
		Description: "the agent responsible to search the internet for info",
		Instruction: `
		You are a research agent.

		INSTRUCTIONS:
		- Assist ONLY with research-related tasks. DO NOT do any math
		- After you're done, with your tasks, respond to the supervisor directly
		- Respond ONLY with the results of your work, do NOT include ANY other text.
		`,
		Model: m,
		ToolsConfig: adk.ToolsConfig{
			ToolsNodeConfig: compose.ToolsNodeConfig{
				Tools: []tool.BaseTool{searchTool},
				UnknownToolsHandler: func(ctx context.Context, name, input string) (string, error) {
					return fmt.Sprintf("unknow tool: %s", name), nil
				},
			},
		},
	})

}

// buildSubtractAgent builds a math subtraction agent.
func buildSubtractAgent(ctx context.Context) (adk.Agent, error) {
	m := model.NewChatModel()

	type subtractReq struct {
		A float64 `json:"a"`
		B float64 `json:"b"`
	}

	type subtractResp struct {
		Result float64
	}

	subtract := func(ctx context.Context, req *subtractReq) (*subtractResp, error) {
		return &subtractResp{
			Result: req.A - req.B,
		}, nil
	}

	subtractTool, err := tools.SafeInferTool("subtract", "subtract two numbers", subtract)
	if err != nil {
		return nil, err
	}

	return adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
		Name:        "subtract_agent",
		Description: "the agent responsible to do math subtractions",
		Instruction: `
		You are a math substraction agent.

		INSTRUCTIONS:
		- Assist ONLY with math subtraction-related tasks
		- After you're done with you tasks, respond to the supervisor directly
		- Respond ONLY with the results of your work, do NOT include ANY other text.
		`,
		Model: m,
		ToolsConfig: adk.ToolsConfig{
			ToolsNodeConfig: compose.ToolsNodeConfig{
				Tools: []tool.BaseTool{subtractTool},
				UnknownToolsHandler: func(ctx context.Context, name, input string) (string, error) {
					return fmt.Sprintf("unknow tool: %s", name), nil
				},
			},
		},
	})
}

// buildMultiplyAgent builds a math multiplication agent.
func buildMultiplyAgent(ctx context.Context) (adk.Agent, error) {
	m := model.NewChatModel()

	type multiplyReq struct {
		A float64 `json:"a"`
		B float64 `json:"b"`
	}

	type multiplyResp struct {
		Result float64
	}

	multiply := func(ctx context.Context, req *multiplyReq) (*multiplyResp, error) {
		return &multiplyResp{
			Result: req.A * req.B,
		}, nil
	}

	multiplyTool, err := tools.SafeInferTool("multiply", "multiply two numbers", multiply)
	if err != nil {
		return nil, err
	}

	return adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
		Name:        "multiply_agent",
		Description: "the agent responsible to do math multiplications",
		Instruction: `
		You are a math multiplication agent.

		INSTRUCTIONS:
		- Assist ONLY with math multiplication-related tasks
		- After you're done with you tasks, respond to the supervisor directly
		- Respond ONLY with the results of your work, do NOT include ANY other text.
		`,
		Model: m,
		ToolsConfig: adk.ToolsConfig{
			ToolsNodeConfig: compose.ToolsNodeConfig{
				Tools: []tool.BaseTool{multiplyTool},
				UnknownToolsHandler: func(ctx context.Context, name, input string) (string, error) {
					return fmt.Sprintf("unknow tool: %s", name), nil
				},
			},
		},
	})
}

// buildDivideAgent builds a math division agent.
func buildDivideAgent(ctx context.Context) (adk.Agent, error) {
	m := model.NewChatModel()

	type divideReq struct {
		A float64 `json:"a"`
		B float64 `json:"b"`
	}

	type divideResp struct {
		Result float64
	}

	divide := func(ctx context.Context, req *divideReq) (*divideResp, error) {
		if req.B == 0 {
			return nil, errors.New("division by zero")
		}
		return &divideResp{
			Result: req.A / req.B,
		}, nil
	}

	divideTool, err := tools.SafeInferTool("divide", "divide two numbers", divide)
	if err != nil {
		return nil, err
	}

	return adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
		Name:        "divide_agent",
		Description: "the agent responsible to do math divisions",
		Instruction: `
		You are a math division agent.

		INSTRUCTIONS:
		- Assist ONLY with math division-related tasks
		- After you're done with you tasks, respond to the supervisor directly
		- Respond ONLY with the results of your work, do NOT include ANY other text.
		`,
		Model: m,
		ToolsConfig: adk.ToolsConfig{
			ToolsNodeConfig: compose.ToolsNodeConfig{
				Tools: []tool.BaseTool{divideTool},
				UnknownToolsHandler: func(ctx context.Context, name, input string) (string, error) {
					return fmt.Sprintf("unknow tool: %s", name), nil
				},
			},
		},
	})
}

// buildMathAgent builds a math agent that manages three agents: subtract, multiply, and divide.
func buildMathAgent(ctx context.Context) (adk.Agent, error) {
	m := model.NewChatModel()

	sa, err := buildSubtractAgent(ctx)
	if err != nil {
		return nil, err
	}

	ma, err := buildMultiplyAgent(ctx)
	if err != nil {
		return nil, err
	}

	da, err := buildDivideAgent(ctx)
	if err != nil {
		return nil, err
	}

	mathAgent, err := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
		Name:        "math_agent",
		Description: "the agent responsible to do math",
		Instruction: `
		You are a math agent.

		INSTRUCTIONS:
		- Assist ONLY with math-related tasks
		- After you're done with your tasks, respond to the supervisor directly
		- Respond ONLY with the results of your work, do NOT include ANY other text.
		- YOU are yourself also a supervisor managing three agents:
		- an subtract agent, a multiple_agent, a divide_agent. Assign math-related tasks to these agents.
		- Assisgn work to one agent at a time, do not call agents in parallel.
		- Do not do any real math work yourself, alwasy transfer to your sub agents to do actual computation.
		`,
		Model: m,
		ToolsConfig: adk.ToolsConfig{
			ToolsNodeConfig: compose.ToolsNodeConfig{
				UnknownToolsHandler: func(ctx context.Context, name, input string) (string, error) {
					return fmt.Sprintf("unknow tool: %s", name), nil
				},
			},
		},
	})

	return supervisor.New(ctx, &supervisor.Config{
		Supervisor: mathAgent,
		SubAgents:  []adk.Agent{sa, ma, da},
	})
}

func buildSupervisor(ctx context.Context) (adk.Agent, error) {
	m := model.NewChatModel()

	sv, err := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
		Name:        "supervisor",
		Description: "the agent responsible to supervise tasks",
		Instruction: `
		Your are a supervisor managing two agents:

		- a research agent. Assign research-related tasks to this agent
		- a math agent. assign math-related tasks to this agent
		Assign work to one agent at a time, do not call agents in parallel.
		Do not do any work yourself.
		`,
		Model: m,
		ToolsConfig: adk.ToolsConfig{
			ToolsNodeConfig: compose.ToolsNodeConfig{
				UnknownToolsHandler: func(ctx context.Context, name, input string) (string, error) {
					return fmt.Sprintf("unkonw tool: %s", name), nil
				},
			},
		},
		Exit: &adk.ExitTool{},
	})

	if err != nil {
		return nil, err
	}

	searchAgent, err := buildSearchAgent(ctx)
	if err != nil {
		return nil, err
	}
	mathAgent, err := buildMathAgent(ctx)
	if err != nil {
		return nil, err
	}
	return supervisor.New(ctx, &supervisor.Config{
		Supervisor: sv,
		SubAgents:  []adk.Agent{searchAgent, mathAgent},
	})
}
