import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout


class Cliente(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        client.register_plugin('xep_0077') # In-band Registration
        

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()

    def RegisterUser(self):
        print('register')
        # if 
        # iq = client.Iq()
        # iq['type'] = 'set'
        # iq['register']['username'] = username
        # iq['register']['password'] = password
        # iq['register']['name'] = name
        # iq['register']['email'] = email
        # iq.send(now=True, timeout=TIMEOUT)

    def Login(self):
        if self.connect():
            self.process()
            print('success')
        else:
            print('error')


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(levelname)-8s %(message)s')

    xmpp = Cliente('Javi@redes2020.xyz', 'javi')

    import ssl
    xmpp.ssl_version = ssl.PROTOCOL_TLS

    menu = '0. Salir\n1. Registrar nuevo usuario.\n2. Iniciar sesion\n'
    opcion = ''
    
    while opcion != '0':
        opcion = input(menu)

        if opcion == '1':
            print('')
        elif opcion == '2':
            xmpp.Login()
        elif opcion == '0':
            xmpp.disconnect()
    # if xmpp.connect():
    #     xmpp.process()
    #     print('success')