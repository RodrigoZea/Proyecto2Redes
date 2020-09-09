import logging
from argparse import ArgumentParser
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
import sleekxmpp

class Client(ClientXMPP):
    """ INIT """
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        
        # Handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("register", self.register)

        # Plugins
        # Registration order doesnt matter so...
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0030') # Service Disc
        self.register_plugin('xep_0077') # In-band Register
        self.register_plugin('xep_0066') # Ping

    """ HANDLER RELATED """
    async def start(self, event):
        self.send_presence()
        self.get_roster()

    async def message(self, msg):
        print(msg)

    # Basado del siguiente ejemplo
    # https://searchcode.com/file/58168360/examples/register_account.py/
    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        print(resp)
        try:
            resp.send(now=True)
            print("Account created for", self.boundjid, '!')
        except IqError as e:
            print("Could not register account:", e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()

    """ OTHER DEFS """
    def login(self):
        if self.connect():
            self.process()
            print("logged in")
        else:
            print("error: couldnt log in")

if __name__ == '__main__':
    # Hardcode domain since it wont change
    domain = '@redes2020.xyz'

    # Ask user for username and pass via parameters
    # Setup the command line arguments.
    parser = ArgumentParser()

     # Output verbosity options.
    parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                        action="store_const", dest="loglevel",
                        const=logging.ERROR, default=logging.INFO)
    parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                        action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid",
                        help="JID to use")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")
    parser.add_argument("-n", "--nick", dest="nick",
                        help="nickname")

    args = parser.parse_args()

    # Setup logging
    #logging.basicConfig(level=args.loglevel,format='%(levelname)-8s %(message)s')

    
    xmpp = Client(args.nick + domain, args.password)
    if xmpp.connect():
        xmpp.process(block=True)
        print("Done")
    else:
        print("no c puede conectar")

    print('1. Registrar nueva cuenta.')
    print('2. Iniciar sesion.')
    print('3. Cerrar sesion.')
    print('4. Eliminar cuenta')

"""
Registrar una cuenta nueva en el servidor.
Iniciar sesion con una cuenta.
Cerrar sesion con una cuenta.
Eliminar la cuenta del servidor.

Mostrar todos los usuarios / contactos y su estado.
Agregar un usuario a los contactos.
Mostrar detalles de contacto de un usuario.
Comunicación 1 a 1 con cualquier usuario / contacto.
Participar en conversaciones grupales.
Definir mensaje de presencia.
Enviar / recibir notificaciones.
Enviar / recibir archivos.
"""