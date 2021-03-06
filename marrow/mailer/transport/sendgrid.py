# encoding: utf-8

import urllib

from marrow.mailer.exc import MailConfigurationException, DeliveryFailedException, MessageFailedException

__all__ = ['SendgridTransport']

log = __import__('logging').getLogger(__name__)


class SendgridTransport(object):
    __slots__ = ('ephemeral', 'user', 'key')
    
    def __init__(self, config):
        self.user = config.get('user')
        self.key = config.get('key')
    
    def startup(self):
        pass
    
    def deliver(self, message):

        to = message.to

        # Sendgrid doesn't accept CC over the api
        if message.cc:
            to.extend(message.cc)

        args = dict({
                'api_user': self.user,
                'api_key': self.key,
                'from': [fromaddr.address.encode(message.encoding) for fromaddr in message.author],
                'fromname': [fromaddr.name.encode(message.encoding) for fromaddr in message.author],
                'to': [toaddr.address.encode(message.encoding) for toaddr in to],
                'toname': [toaddr.name.encode(message.encoding) for toaddr in to],
                'subject': message.subject.encode(message.encoding),
                'text': message.plain.encode(message.encoding)
            })

        if message.bcc:
            args['bcc'] = [bcc.address.encode(message.encoding) for bcc in message.bcc]
        
        if message.reply:
            args['replyto'] = message.reply.address.encode(message.encoding)
        
        if message.rich:
            args['html'] = message.rich.encode(message.encoding)
        
        if message.attachments:
            # Not implemented yet
            """
            attachments = []
            
            for attachment in message.attachments:
                attachments.append((
                        attachment['Content-Disposition'].partition(';')[2],
                        attachment.get_payload(True)
                    ))
            
            msg.attachments = attachments
            """
            raise MailConfigurationException()

        try:
            response = urllib.urlopen("https://sendgrid.com/api/mail.send.json?" + urllib.urlencode(args, True))
        except IOError:
            raise DeliveryFailedException(message, "Could not connect to Sendgrid.")
        else:
            respcode = response.getcode()
            if respcode >= 400 and respcode <= 499:
                raise MessageFailedException(response.read())
            elif respcode >= 500 and respcode <= 599:
                raise DeliveryFailedException(message, "Sendgrid service unavailable.")
    
    def shutdown(self):
        pass
