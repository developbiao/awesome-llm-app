package main

import (
	"context"
	"log"

	"github.com/cloudwego/eino/components/prompt"
	"github.com/cloudwego/eino/schema"
)

func createTemplate() prompt.ChatTemplate {
	// Create  template using FString
	return prompt.FromMessages(schema.FString,
		// System message template
		schema.SystemMessage("You are a {role}. Please respond in a {style} tone. Your goal is to keep developers positive and optimistic while offering technical advice and caring about their mental well-being."),
		// Insert conversation history (omit for a new conversation)
		schema.MessagesPlaceholder("chat_history", true),
		// User message template
		schema.UserMessage("Qeustion: {question}"),
	)
}

func createMessagesFromTemplate() []*schema.Message {
	template := createTemplate()
	// Render messages from the template
	messages, err := template.Format(context.Background(), map[string]any{
		"role":     "Programmer Encouragement Assistant",
		"style":    "positive, warm, and professional",
		"question": "My code keeps throwing errors and I feel frustrated. What should I od?",
		// Dialogue history (simulate two rounds)
		"chat_history": []*schema.Message{
			schema.UserMessage("Hi"),
			schema.AssistantMessage("Hey! I'm your encouragement assistant! Remember, every great enginner grows through debugging. How can I help?", nil),
			schema.UserMessage("I think my code is terrible"),
			schema.AssistantMessage("Every developer feels that way at times! What matters is continuous learning and improvement. Let's review the code together - I'm confident with refactoring and optimization it'll et better. Remeber, Rome wasn't built in a day; code quality improves with continuous effort.", nil),
		},
	})

	if err != nil {
		log.Fatalf("format template: %v", err)
	}

	return messages

}

// func main() {
// 	messages := createMessagesFromTemplate()
// 	fmt.Printf("formatted message: %v", messages)
// }
