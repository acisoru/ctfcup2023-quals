package app

import (
	"novosti/app/filters"
	"novosti/app/review"
	"novosti/app/storage"
	"os"
	"strings"

	"github.com/dpapathanasiou/go-recaptcha"
	"github.com/revel/revel"
)

// Build variables
var (
	AppVersion string
	BuildTime  string
)

// Global state
var (
	NewsRepository *storage.NewsRepository
	ReviewQueue    *review.Queue
	AdminToken     string
)

func init() {
	revel.Filters = []revel.Filter{
		revel.PanicFilter,             // Recover from panics and display an error page instead.
		revel.RouterFilter,            // Use the routing table to select the right Action
		revel.FilterConfiguringFilter, // A hook for adding or removing per-Action filters.
		revel.ParamsFilter,            // Parse parameters into Controller.Params.
		revel.SessionFilter,           // Restore and write the session cookie.
		revel.FlashFilter,             // Restore and write the flash cookie.
		revel.ValidationFilter,        // Restore kept validation errors and save new ones from cookie.
		filters.I18nFilter,            // Resolve the requested language
		HeaderFilter,                  // Add some security based headers
		revel.InterceptorFilter,       // Run interceptors around the action.
		revel.CompressFilter,          // Compress the result.
		revel.BeforeAfterFilter,       // Call the before and after filter functions
		revel.ActionInvoker,           // Invoke the action.
	}

	revel.OnAppStart(initRepo)
	revel.OnAppStart(initQueue)
	revel.OnAppStart(initAdminToken)
	revel.OnAppStart(initRecaptcha)
}

func initRepo() {
	directory := os.Getenv("STORAGE_DIR")
	if directory == "" {
		panic("STORAGE_DIR env var is empty, news repository will fail")
	}

	NewsRepository = storage.NewNewsRepository(directory)
}

func initQueue() {
	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		panic("REDIS_ADDR env var is empty, queueing story reviews will fail")
	}

	ReviewQueue = review.NewQueue(redisAddr, "news")
}

func initAdminToken() {
	tokenFile := os.Getenv("ADMIN_TOKEN_FILE")
	if tokenFile == "" {
		panic("ADMIN_TOKEN_FILE env var is empty, admin will not be able to view shared news")
	}

	data, err := os.ReadFile(tokenFile)
	if err != nil {
		panic("unable to read ADMIN_TOKEN_FILE, admin will not be able to view shared news")
	}

	AdminToken = strings.TrimSpace(string(data))
}

func initRecaptcha() {
	recaptchaPrivateKey := os.Getenv("RECAPTCHA_PRIVATE_KEY")
	if recaptchaPrivateKey == "" {
		panic("RECAPTCHA_PRIVATE_KEY env var is empty, sharing will fail")
	}

	recaptcha.Init(recaptchaPrivateKey)
}

var HeaderFilter = func(c *revel.Controller, fc []revel.Filter) {
	c.Response.Out.Header().Add("X-Frame-Options", "SAMEORIGIN")
	c.Response.Out.Header().Add("Content-Security-Policy", "default-src 'self'; base-uri 'none'; object-src 'none'; script-src 'self' 'unsafe-inline' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/; style-src 'self' 'unsafe-inline'; frame-src 'self' https://www.google.com/recaptcha/ https://recaptcha.google.com/recaptcha/;")

	fc[0](c, fc[1:])
}
