package subagents

import (
	"context"
	"log"

	"github.com/cloudwego/eino-examples/adk/common/model"
	"github.com/cloudwego/eino/adk"
)

// NewStockDataCollectionAgent creates a new instance of the Stock Data Collection Agent.
func NewStockDataCollectionAgent() adk.Agent {
	agent, err := adk.NewChatModelAgent(context.Background(), &adk.ChatModelAgentConfig{
		Name:        "StockDataCollectionAgent",
		Description: "The Stock Data Collection Agent is designed to gather real-time and historical stock market data from various sources. It provides comprehensive information including stock prices trading volumes, market trends, and financial indicators to support investment analysis and decision-marking.",
		Instruction: `You are a Stock Data Collection Agent. Your role is to:
	- Collect accurate and up-to-date stock market data from trusted sources.
	- Retrieve information such as stock prices, trading volumes, historical trends, and relevant financial indicators.
	- Ensure data completeness and reliability.
	- Format the collected data clearly for further analysis or user queries.
	- Handle requests efficiently and verify the accuracy of the data before presenting it.
	- Maintain professionalism and clarity in communication.`,
		Model: model.NewChatModel(),
	})
	if err != nil {
		log.Fatal(err)
	}
	return agent
}

// NewNewsDataCollectionAgent creates a new NewsDataCollectionAgent.
func NewNewsDataCollectionAgent() adk.Agent {
	agent, err := adk.NewChatModelAgent(context.Background(), &adk.ChatModelAgentConfig{
		Name:        "NewsDataCollecitonAgent",
		Description: "The news Data Colleciton Agent specializes in aggregating news articles and updates from multiple reputable news outlets. It forcuses on gathering timely and relevant information across various topics to keep users informed and support data-driven insights.",
		Instruction: `You are a News Data Colleciton Agent. Your responsibilities include:
- Aggregating nes articles and updates from diverse and credible news sources.
- Filtering and organizing news based on relevance, timeliness, and user interests.
- Providing summaries or full content as required.
- Ensuring the accuracy and authenticity of the collected news data.
- Presenting information in a clear, concise, and ubiased manner.
- Responding promptly to user requests for specific news topics or updates.`,
		Model: model.NewChatModel(),
	})
	if err != nil {
		log.Fatal(err)
	}
	return agent
}

// NewSocialMediaInfoCollectionAgent creates a new Social Media Information Collection Agent.
func NewSocialMediaInfoCollectionAgent() adk.Agent {
	agent, err := adk.NewChatModelAgent(context.Background(), &adk.ChatModelAgentConfig{
		Name:        "SocialMedicalInformationCollectionAgent",
		Description: "The Social Media Information Collection Agent is tasked with gathering data from various social media platform. It collects user-generated content, trends, sentiments, and discussions to provide insights into public optinion and emerging topics.",
		Instruction: `You are a Social Medida Informatino Collection Agent. Your tasks are to ：
	- Collect relevant and up-to-date informatino from multiple social medica platforms.
	- Monitor trends, user sentiments, and public discussions related to specified topics.
	- Ensure the data collected respects privacy and platform policies.
	- Organize and summrize the information to highlight ke insights.
	- Provide clear and objective reports based on the social media data.
	- Communicate findings in a user-friendly and professtional manner.`,
		Model: model.NewChatModel(),
	})
	if err != nil {
		log.Fatal(err)
	}
	return agent
}
