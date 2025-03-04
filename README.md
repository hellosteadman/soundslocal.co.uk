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

The build process expects a `js/start.js` file and an `scss/start.scsss` file to be in the `theme` directory. You should be able to use ES6 syntax in any .js file imported by `start.js`, and likewise any SCSS imported via `start.sscs`. These files are compiled as part of the build process.

### A note on NodeJS requirements

I've ignored `package.json` and `package-lock.json` in the repo as Budgie will try and create the necessary infrastructure itself. But it shouldn't complain if you have your own `package.json` file, and will only try and install dependencies it doesn't have (it's a naive approach, just checking the `devDependencies` list).

## Running the develompent server

Running `python manage.py serve` will start the development server at `http://localhost:8000`. You can set the host and port to something differenet if you need to.

The first time you access a JS or SCSS resource (as per the build section above), that respective file will be compiled. Right now it'll only compile the first time, so if you make changes to JS and/or SCSS, you'll need to restart the dev server. I might improve that in the future.

## Plugins

There are currently 3 plugins (one of them is referenced by naother so doesn't need to be declared in settings):

### `budgie.contrib.markdown`

Provides a `markdown` template filter.

### `budgie.contrib.nodejs`

Provides an interface into NodeJS, handling compilation of JS and SCSS files. This doesn't need to be declared in settings, as it's imported by other plugins.

### `budgie.contrib.statifiles`

Handles serving static files via the dev server, and building them as part of the build process.
