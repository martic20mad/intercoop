# -*- encoding: utf-8 -*-

from flask import (
    make_response,
    request,
    Response
    )

from . import apiclient
from . import peerdatastorage
from .perfume import Perfume, route
from yamlns import namespace as ns

"""
# TODO:

- Solve translations
- No service description
- No service name
- No such service
- Include peer.info optionally
"""



template = u"""\
<html>
<head>
<meta encoding='utf-8' />
<title>{}</title>
</head>
<body>
<h1>Intercooperación</h1>
<ul>
{}</ul>
</body>
</html>
"""




class Portal(Perfume):

    def __init__(self, name, peerdata):
        super(Portal, self).__init__(name)
        self.peers = peerdatastorage.PeerDataStorage(peerdata)
        self.name = name

    def serviceDescription(self, peer, service):
        return u"""\
<div class='service'>
<a href='activateservice/{peer.peerid}/{serviceid}'>
<div class='service_header'>{service.name.es}</div>
<div class='service_description'>{service.description.es}</div>
</a>
</div>
""".format(
    peer = peer,
    serviceid = service,
    service = peer.services[service],
    language='es',
    )

    def peerDescription(self, peer):
        return u"""\
<div class='peer'>
<div class='peerlogo'><img src='{peer.logo}' /></div>
<div class='peerheader'><a href='{peer.url.es}'>{peer.name}</a></div>
<div class='peerdescription'>{peer.description.es}</div>
<div class='services'>
""".format(peer=peer) + "".join(
    self.serviceDescription(peer, service)
    for service in peer.services
)+u"""\
</div>
</div>
"""

    @route('/', methods=['GET'])
    def index(self):
        response = template.format(
            self.name,
            "".join(
                self.peerDescription(peer)
                for peer in self.peers
                )
            )
        return response


# vim: ts=4 sw=4 et
