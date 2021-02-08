""" TODO """

from urllib.parse import urlencode

from babel.dates import format_date
from slugify import slugify

from cubersio import app
from cubersio.util.events.mbld import build_mbld_results
from cubersio.util.times import convert_centiseconds_to_friendly_time


@app.context_processor
def link_to_algcubingnet():
    """ Generates an anchor with a link to alg.cubing.net for the specified set and algorithm/moves. """

    def __link_to_algcubingnet(setup, alg, moves_count):
        """ Generates an anchor with a link to alg.cubing.net for the specified set and algorithm/moves. """

        # If no solution was provided, the solve probably predated the required FMC solutions feature
        # Don't render a link to alg.cubing.net; instead just render the moves count
        if not alg:
            return moves_count

        anchor = '<a href="https://alg.cubing.net/?{}" style="font-size: 14px;" target="_blank">{} <i class="fas fa-external-link-alt"></i></a>'
        querystring = urlencode([
            ('setup', setup),
            ('alg', alg),
            ('type', 'reconstruction'),
        ])

        return anchor.format(querystring, moves_count)

    return dict(link_to_algcubingnet=__link_to_algcubingnet)


@app.template_filter('slugify')
def slugify_filter(value):
    """ Jinja custom filter to slugify a string. """

    return slugify(value)


@app.template_filter('format_datetime')
def format_datetime(value):
    """ Jinja custom filter to format a date to Apr 1, 2018 format. """

    return format_date(value, locale='en_US')


@app.template_filter('friendly_time')
def friendly_time(value):
    """ Jinja custom filter to convert a time in cs to a user-friendly time. """

    if value is None:
        return ''

    try:
        converted_value = int(value)
    except ValueError:
        return value
    return convert_centiseconds_to_friendly_time(converted_value)


@app.template_filter('format_fmc_result')
def format_fmc_result(value):
    """ Jinja custom filter to convert a fake 'centisecond' result to FMC moves. """

    if value is None:
        return ''

    try:
        converted_value = int(value) / 100
    except ValueError:
        return value

    if converted_value == int(converted_value):
        converted_value = int(converted_value)

    return converted_value


@app.template_filter('format_mbld_result')
def format_mbld_result(value):
    """ Jinja custom filter to convert a fake 'centisecond' result to MBLD results. """

    if value is None:
        return ''

    if not value:
        return ''

    return build_mbld_results(value)
