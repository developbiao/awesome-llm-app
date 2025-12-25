package main

import (
	"context"

	"github.com/cloudwego/eino/components/prompt"
	"github.com/cloudwego/eino/schema"
	"learn.example.agent/internal/logs"
)

func main() {
	systemTpl := `你是情绪助手，你的任务是根据用户的输入，生成一段赞美的话，语句优美，韵律强，具体人文关怀。
用户昵称: {user_nickname}
用户年龄: {user_age}
用户性别: {user_gender}
用户喜好: {user_hobby}`

	chatTpl := prompt.FromMessages(schema.FString,
		schema.SystemMessage(systemTpl),
		schema.MessagesPlaceholder("message_histories", true),
		schema.UserMessage("{user_query}"),
	)

	msgList, err := chatTpl.Format(context.Background(), map[string]any{
		"user_nickname": "John Doe",
		"user_age":      30,
		"user_gender":   "male",
		"user_hobby":    "reading",
		"message_histories": []*schema.Message{
			schema.UserMessage("I like play piano"),
			schema.AssistantMessage("You are a talented musician!", nil),
		},
		"user_query": "请为我即兴赋诗一首",
	})

	if err != nil {
		logs.Errorf("Format failed, err=%v", err)
		return
	}

	logs.Infof("Rendered Messages:")
	for _, msg := range msgList {
		logs.Infof("- %v", msg)
	}

}
