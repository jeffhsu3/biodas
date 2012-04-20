from tastypie.exceptions import NotFound, BadRequest

def parse_das_segment(request):
    """ Parse a das request
    """
    if request.POST:
        seg = request.POST.get('segment')
    if request.GET:
        seg = request.GET.get('segment')
    # :TODO make sure start does not exceed segment end
    reference = seg.split(":")[0]
    try:
        temp = seg.split(":")[1]
    except IndexError:
        return (reference, None, None)
    try:
        start = int(temp.split(",")[0])
        end = int(temp.split(",")[1])
        return (reference, start, end)
    except ValueError:
        raise BadRequest("Invalid segment provided, must be of form \
                features?segment=reference:start,stop")


def add_das_headers(response, version = '1.6', **kwargs):
    """ Add DAS specification headers
    """
    if version == 2:
        # :TODO BioDAS 2 specifications
        response['Content-Type'] = 'text/xml'
    else:
        response['Content-Type'] = 'text/xml'
    # :TODO make to specific sources
    response['X-DAS-Version'] = 'DAS/%s' % version
    response['X-DAS-Status'] = 200
    response['X-DAS-Capabilities'] = 'features/1.0;'
    response['X-DAS-Server'] = 'django-biodas'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Expose-Headers'] =\
            'X-DAS-Version, X-DAS-Status, X-DAS-Capabilities, X-DAS-Server'
    return response
