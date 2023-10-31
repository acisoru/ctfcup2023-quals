package controllers

import (
	"errors"
	"novosti/app"
	"novosti/app/routes"
	"novosti/app/storage"
	"strings"

	"github.com/revel/revel"
)

const adminTokenCookie = "_ADMIN_TOKEN"

// Admin is the main admin app controller.
type Admin struct {
	*revel.Controller
}

// View implements the admin-only news viewing endpoint.
func (c Admin) View(id string) (result revel.Result) {
	cookie, err := c.Request.Cookie(revel.CookiePrefix + adminTokenCookie)
	if err != nil || cookie.GetValue() != app.AdminToken {
		c.Log.Warn("non-admin tried to access admin endpoint", "ip", c.Request.Header.Get("CF-Connecting-IP"))
		return c.NotFound("No matching route found: " + c.Request.GetRequestURI())
	}

	var title string
	var content string

	defer func() {
		if result != nil {
			return
		}

		c.ViewArgs["storyID"] = id
		result = c.Render(title, content)
	}()

	story, err := app.NewsRepository.GetStory(storage.StoryID(id))
	if errors.Is(err, storage.ErrNotFound) {
		return c.NotFound("No such story exists")
	} else if err != nil {
		c.Log.Error("unexpected error while getting story from repository", "error", err)
		c.ViewArgs["error"] = revel.Message(c.Request.Locale, "app.error.view")
		return c.Redirect(routes.News.Share())
	}

	title = story.Title
	content = strings.Replace(story.Content, "\n", "<br>", -1)

	return
}
