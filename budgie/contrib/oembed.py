from budgie import app
import re


URL_PATTERN = re.compile(r'^(https?://[^\s]+)$')
PROVIDERS = (
    {
        'patterns': (
            r'^https?://(?:www\.)?youtube\.com/watch\?(?:.+&)?v=([^&$]+)',
            r'^https?://youtu\.be\/(.+)(?:\?|$)'
        ),
        'html': '<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/%s" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    },
    {
        'patterns': (
            r'^https?://([^\.]+)\.castos\.com/player/(.+)(?:\?|$)',
        ),
        'html': '<iframe width="100%" height="150" frameborder="no" scrolling="no" src="https://%s.castos.com/player/%s" title="Episode audio player" seamless></iframe>'
    },
    {
        'patterns': (
            r'^https://anchor\.fm/([^/]+)/embed/episodes/(.+)(?:\?|$)',
            r'^https://podcasters\.spotify\.com/pod/show/([^\/]+)/embed/episodes/(.+)(?:\?|$)'
        ),
        'html': '<iframe width="100%" height="100" frameborder="no" scrolling="no" src="https://anchor.fm/%s/embed/episodes/%s" title="Episode audio player" seamless></iframe>'
    },
    {
        'patterns': (
            r'https://webplayer\.whooshkaa\.com/player/episode/id/(\d+)',
            r'https://player\.whooshkaa\.com/episode/?\?(?:.*&)?id=(\d+)'
        ),
        'html': '<iframe width="100%" height="200" frameborder="no" scrolling="no" src="https://webplayer.whooshkaa.com/player/episode/id/%s" title="Episode audio player" seamless></iframe>'
    },
    {
        'patterns': (
            r'https://playlist\.megaphone\.fm/\?(?:.*&)?e=(.+)(?:\?|$)',
        ),
        'html': '<iframe width="100%" height="200" frameborder="no" scrolling="no" src="https://playlist.megaphone.fm/?e=%s" title="Episode audio player" seamless></iframe>'
    },
    {
        'patterns': (
            r'https://widget\.spreaker\.com/player\?episode_id=(\d+)',
        ),
        'html': '<iframe width="100%" height="200" frameborder="no" scrolling="no" src="https://widget.spreaker.com/player?episode_id=%s" title="Episode audio player" seamless></iframe>'
    },
    {
        'patterns': (
            r'https://embed.simplecast.com/(.+)(?:\?|$)',
        ),
        'html': '<iframe width="100%" height="200" frameborder="no" scrolling="no" src="https://embed.simplecast.com/%s" title="Episode audio player" seamless></iframe>'
    },
    {
        'patterns': (
            r'^https?://share\.transistor\.fm/s/(.+)(?:\?|$)',
            r'^https?://media\.transistor\.fm/([^/]+)/[^\.]+\.mp3$'
        ),
        'html': '<iframe width="100%" height="180" frameborder="no" scrolling="no" src="https://share.transistor.fm/e/%s" title="Episode audio player" seamless></iframe>'
    },
    {
        'patterns': (
            r'^https?://player\.captivate\.fm/episode/([\w-]+)',
        ),
        'html': '<iframe width="100%" height="180" frameborder="no" scrolling="no" src="https://player.captivate.fm/episode/%s" title="Episode audio player" seamless></iframe>'
    },
    {
        'patterns': (
            r'^https?://share\.fireside\.fm/episode/(\w+\+\w+)',
        ),
        'html': '<iframe src="https://player.fireside.fm/v2/%s?theme=light" width="100%" height="200" title="Episode audio player" frameborder="0" scrolling="no"></iframe>'
    },
    {
        'patterns': (
            r'^https?://(?:www\.)?vimeo\.com/(\d+)',
        ),
        'html': '<iframe width="560" height="315" src="https://player.vimeo.com/video/%s?badge=0&amp;autopause=0&amp;player_id=0" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" title="Vimeo video player" allowfullscreen></iframe>'
    },
    {
        'patterns': (
            r'^https://bandcamp.com/EmbeddedPlayer/(.+)',
        ),
        'html': '<iframe width="560" height="120" src="https://bandcamp.com/EmbeddedPlayer/%s" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" title="BandCamp player" allowfullscreen></iframe>'
    },
    {
        'patterns': (
            r'https://podcasts\.apple\.com(?:/.+)?/podcast(?:/.+)?/id(\d+)\?(?:.*&.*)?i=(\d+)',
        ),
        'html': '<iframe width="100%" height="175" src="https://embed.podcasts.apple.com/podcast/id%s?i=%s&theme=dark" frameborder="0" sandbox="allow-same-origin allow-scripts allow-top-navigation-by-user-activation" allow="encrypted-media *; clipboard-write" title="Apple Podcasts player"></iframe>'
    },
    {
        'patterns': (
            r'^https?://(?:www\.)?tiktok\.com/@[^/]+/video/(\d+)',
        ),
        'html': '<iframe width="315" height="560" src="https://www.tiktok.com/embed/v2/%s" title="TikTok video player" frameborder="0" allow="autoplay; encrypted-media"></iframe>',
        'ratio': '9x16'
    }
)


def resolve(url):
    for provider in PROVIDERS:
        for pattern in provider['patterns']:
            ratio = provider.get('ratio', '16x9')
            if match := re.match(pattern, url):
                return '<div class="oembed ratio ratio-%s">%s</div>' % (
                    ratio,
                    provider['html'] % match.groups()
                )

    return '<a href="%(url)s" target="_blank">%(url)s</a>' % {
        'url': url
    }


@app.transformer('article_body', 90)
def oembed_transformer(value):
    if value:
        lines = []

        for line in value.splitlines():
            if match := URL_PATTERN.fullmatch(line):
                lines.append(
                    resolve(match.groups()[0])
                )
            else:
                lines.append(line)

        return '\n'.join(lines)

    return ''
