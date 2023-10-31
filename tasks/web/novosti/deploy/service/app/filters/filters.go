package filters

import "github.com/revel/revel"

// Custom i18n filter which uses Russian by default and
// supports switching to a different language via the cookie.
func I18nFilter(c *revel.Controller, fc []revel.Filter) {
	value := "ru-RU"

	cookie, err := c.Request.Cookie(revel.CookiePrefix + "_LANG")
	if err == nil {
		value = cookie.GetValue()
	}

	c.Request.Locale = value
	c.ViewArgs[revel.CurrentLocaleViewArg] = value

	fc[0](c, fc[1:])
}
