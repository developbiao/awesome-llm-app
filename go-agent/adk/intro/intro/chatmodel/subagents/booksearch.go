package subagents

import (
	"context"
	"log"

	"github.com/cloudwego/eino/components/tool"
	"github.com/cloudwego/eino/components/tool/utils"
)

type BookSearchInput struct {
	Genre     string `json:"genre" jsonschema_description:"Preferred book genre,num=fiction,enum=sci-fi,enum=mystery,enum=biography,enum=business"`
	MaxPages  int    `json:"max_pages" jsonschema_description:"Maximum page length (0 for no limit)"`
	MinRating int    `json:"min_rating" jsonschema_description:"Minimum user rating (0-5 scale)"`
}

type BookSearchOutput struct {
	Books []string
}

// NewBookRecommender creates a new book recommender tool.
func NewBookRecommender() tool.InvokableTool {
	bookSearchTool, err := utils.InferTool("search_book", "Search books based on user preferences",
		func(ctx context.Context, input *BookSearchInput) (output *BookSearchOutput, err error) {
			// Mock book data
			var mockBooks = map[string][]string{
				"fiction":   {"The Great Gatsby", "To Kill a Mockingbird", "1984"},
				"sci-fi":    {"Dune", "Ender's Game", "The Hitchhiker's Guide to the Galaxy"},
				"mystery":   {"The Hound of the Baskervilles", "And Then There Were None", "The Girl with the Dragon Tattoo"},
				"biography": {"Steve Jobs by Walter Isaacson", "The Diary of a Young Girl by Anne Frank", "Becoming by Michelle Obama"},
				"business":  {"The Lean Startup by Eric Ries", "Rich Dad Poor Dad by Robert T. Kiyosaki", "Thinking, Fast and Slow by Daniel Kahneman"},
			}

			if books, ok := mockBooks[input.Genre]; ok {
				return &BookSearchOutput{Books: books}, nil
			}

			// Fallback for unknown genres
			return &BookSearchOutput{Books: []string{"Sorry, no books were found for the specified genre."}}, nil
		},
	)
	if err != nil {
		log.Fatalf("failed to create search book tool: %v", err)
	}
	return bookSearchTool
}
