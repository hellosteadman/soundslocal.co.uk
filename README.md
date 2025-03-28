Sounds Local
============

## Background

This website is built using a static site generator written by [me](https://github.com/hellosteadman). It should work on a standard Python 3 setup, but JS and SCSS compilation needs NodeJS (`node` and `npm` to be precise).

## Budgie

Budgie is my little static site generator. For the moment, it's only intended to build this site, so it has some expectations about structure that might not work for other sites. If there's any demand, I'll setup Budgie as its own package and make it more flexible.

## Setting up

1. Clone the repo into a new clean Python virtual environment.
2. Ensure `node --version` works. I'm developing against `v18.14.1` but it'll likely work in older versions.
3. Ensure `npx --version` works. My version is `9.3.1`.
4. Run `pip install -r requirements.txt`

You should now be able to use the CLI to build the site, or run the development server.

## The `settings.yaml` file

In an effort to make Budgie as flexible as possible, settings can be defined in a simple YAML file. Right now the following settings are supported:

- ` domain`: the domain the site will be served on once built. This domain is used to build all URLs. It can be overridden with the `DOMAIN` environment variable.
- `budgie_plugins`: a list of packages that can extend Budgie's basic functionality, like handling static files and rendering Markdown.
- `frontend_packages`: a list of NPM packages used by SCSS or JS. Both SCSS and JS compilation is fairly simple (using `sass` and `esbuild` respectively, rather than Webpack). You can import packages in JS as you normally would, but in SCSS files, use`@import '<package_name>/file';`.

## Building the site

Running `python manage.py build` will build the site based on content in the `content` directory, and HTML, CSS, and JavaScript in the `theme` directory.

The build process expects a `js/start.js` file and an `scss/start.scss` file to be in the `theme` directory. You should be able to use ES6 syntax in any .js file imported by `start.js`, and likewise any SCSS imported via `start.scss`. These files are compiled as part of the build process.

### A note on NodeJS requirements

I've ignored `package.json` and `package-lock.json` in the repo as Budgie will try and create the necessary infrastructure itself. But it shouldn't complain if you have your own `package.json` file, and will only try and install dependencies it doesn't have (it's a naive approach, just checking the `devDependencies` list).

## Running the development server

Running `python manage.py serve` will start the development server at `http://localhost:8000`. You can set the host and port to something differenet if you need to.

The first time you access a JS or SCSS resource (as per the build section above), that respective file will be compiled. When the file changes, it's recompiled and a signal is sent to the browser to reload.

### Hot reloading

The server uses a cheap-and-cheerful way of handling hot-reload messages. Instead of using websockets (because your humble developer isn't up on async-await in Python like he is in Javascript), a cache of messages is saved in memory and accessed periodically by the browser.

When a "reload" message is put on the stack, the browser either reloads the entire page or refreshes the CSS.

It should trigger when content, templates, JS, or SCSS is changed. I'm sure there's room for improvement, but it works for my purposes.

## Plugins

There are a number of plugins, some considered more important than others:

### `budgie.contrib.accordion`

This allows for marking up sections of copy that should be displayed as a horizontal or vertical accordion. You can mark up a accordion like this:

```md
=== ACCORDION ===

## Item one

Text

## Item two

Text

## Item three

Text

=== END ACCORDION ===

```

### `budgie.contrib.bento`

This allows for marking up sections of copy that should be displayed as a bento box of items (similar to a masonry layout). You can mark up a bento box like this:

```md
=== BENTO BOX ===

### Item one

Text

### Item two

Text

### Item three

Text

=== END BENTO BOX ===

```

Currently, bento boxes can't be nested.

### `budgie.contrib.calendly`

Injects CSS and JS tags to handle Calendly links.

### `budgie.contrib.cta`

Turns markup like this:

```md
[cta url="/contact/"]Contact me[/cta]
```

Into HTML like this:

```html
<p><a href="/contact/" class="btn btn-primary btn-cta">Contact me</a></p>
```

### `budgie.contrib.grids`

This allows for marking up sections of copy that should be displayed as a grid of items. You can mark up a grid like this:

```md
=== GRID OF 3 ITEMS ===

### Item one

Text

### Item two

Text

### Item three

Text

=== END GRID OF 3 ITEMS ===

```

Using the word "items" is optional and arbitrary, and used to form the `class` attribute on grid elements (the grid itself, and each individual cell).

Currently, grids can't be nested.

### `budgie.contrib.icons`

This plugin replaces `:icon:` syntax with an `<i>` element. It's assumed that Bootstrap Icons is the library, and anything in-between the colons is added to the class list, so `:emoji-smile:` becomes `<i class="bi bi-emoji-smile"></i>
`.

### `budgie.contrib.mailerlite`

Injects JS tags to enable MailerLite form support.

### `budgie.contrib.markdown`

Provides a `markdown` template filter. This should definitely be included in `settings.yaml`. This is automatically activated.

### `budgie.contrib.media`

Handles serving media files via the dev server, and building them as part of the build process. It parses Markdown image references and article properties, replacing the string path with a media `File` object. This is automatically activated.

### `budgie.contrib.oembed`

Parses Markdown for links to oEmbeddable resources, like YouTube videos.

### `budgie.contrib.plausible`

Injects JS tags to track traffic via Plausible.io.

### `budgie.contrib.sections`

Works similarly to `budgie.contrib.grids`, but takes any markup and wraps it in a `<div class="section">`.

Similarly to the Grids plugin, you can define waht the section is, like this:

```md
=== ABOUT SECTION ===

About text

=== END ABOUT SECTION ===
```

Unlike the Grids plugin, sections can be nested, although currently you can't indent them in your Markdown. I'd like that to change, for readability.

### `budgie.contrib.staticfiles`

Handles serving static files via the dev server, and building them as part of the build process. This is also essential, so should be in settings.

### `budgie.contrib.nodejs`

Provides an interface into NodeJS, handling compilation of JS and SCSS files. This doesn't need to be declared in settings, as it's imported by other plugins.
