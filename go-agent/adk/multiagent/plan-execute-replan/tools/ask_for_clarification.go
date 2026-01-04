package tools

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"os"

	"github.com/cloudwego/eino/components/tool"
	"github.com/cloudwego/eino/components/tool/utils"
)

type AskForClarificationInput struct {
	Question string `json:"question" jsonschema_description:"The specific question you want to ask the user to get the missing information"`
}

// NewAskForClarificationTool creates a new instance of the AskForClarificationTool.
func NewAskForClarificationTool() tool.InvokableTool {
	t, err := utils.InferOptionableTool(
		"ask_for_clarification",
		"Call this tool when the user's request is ambiguousor lacks the necessary information to proceed. Use it to ask a follow-up question to get the details you need, such as the book's genre, before you can use other tools effectively.",
		func(ctx context.Context, input *AskForClarificationInput, opts ...tool.Option) (output string, err error) {
			fmt.Printf("\nQuestion: %s\n", input.Question)
			scanner := bufio.NewScanner(os.Stdin)
			fmt.Print("\n Your input here:")
			scanner.Scan()
			fmt.Println()
			nInput := scanner.Text()
			return nInput, nil
		})

	if err != nil {
		log.Fatal(err)
	}

	return t
}
