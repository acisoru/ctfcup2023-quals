const path = require("path");

module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    "postcss-copy-assets": {
      pathTransform: (newPath) => {
        return path.join(
          path.dirname(newPath),
          "../../",
          path.basename(path.dirname(newPath)),
          path.basename(newPath)
        );
      },
    },
    ...(process.env.NODE_ENV === "production"
      ? {
          cssnano: {
            preset: [
              "default",
              {
                discardComments: {
                  removeAll: true,
                },
              },
            ],
          },
        }
      : {}),
  },
};
