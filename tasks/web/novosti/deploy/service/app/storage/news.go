package storage

import (
	"encoding/base32"
	"errors"
	"fmt"
	"io/fs"
	"novosti/app/storage/model"
	"os"
	"path/filepath"

	"gitlab.com/NebulousLabs/fastrand"
	"google.golang.org/protobuf/proto"
)

var ErrNotFound = errors.New("entity not found")

// NewsStory represents a single news story saved by the repository.
type NewsStory struct {
	Title   string
	Content string
}

// StoryID is a story identifier constructed from 20 bytes of entropy.
type StoryID string

// NewsRepository provides a file-based storage for saving and retrieving shared news stories.
type NewsRepository struct {
	directory string
}

// NewNewsRepository creates a new news repository which will store the stories in the specified directory.
func NewNewsRepository(directory string) *NewsRepository {
	return &NewsRepository{directory}
}

// CreateStory creates a new story and returns its ID.
func (nr *NewsRepository) CreateStory(story NewsStory) (StoryID, error) {
	data, err := proto.Marshal(&model.NewsStory{Title: story.Title, Content: story.Content})
	if err != nil {
		return StoryID(""), fmt.Errorf("marshaling story model: %w", err)
	}

	id := generateID()

	file, err := os.Create(filepath.Join(nr.directory, string(id)))
	if err != nil {
		return StoryID(""), fmt.Errorf("creating story file: %w", err)
	}

	defer file.Close()

	if _, err := file.Write(data); err != nil {
		return StoryID(""), fmt.Errorf("writing story file: %w", err)
	}

	return id, nil
}

// GetStory gets an existing story by its ID.
func (nr *NewsRepository) GetStory(id StoryID) (NewsStory, error) {
	data, err := os.ReadFile(filepath.Join(nr.directory, string(id)))
	if errors.Is(err, fs.ErrNotExist) {
		return NewsStory{}, ErrNotFound
	} else if err != nil {
		return NewsStory{}, fmt.Errorf("reading story file: %w", err)
	}

	var story model.NewsStory
	if err := proto.Unmarshal(data, &story); err != nil {
		return NewsStory{}, fmt.Errorf("unmarshaling story model: %w", err)
	}

	return NewsStory{Title: story.Title, Content: story.Content}, nil
}

var idEncoding = base32.StdEncoding.WithPadding(base32.NoPadding)

func generateID() StoryID {
	return StoryID(idEncoding.EncodeToString(fastrand.Bytes(20)))
}
