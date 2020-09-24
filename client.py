import logging
import threading
import base64
from argparse import ArgumentParser
from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
from sleekxmpp.exceptions import IqError, IqTimeout
import sleekxmpp

class Register(ClientXMPP):
    """ INIT """
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        
        # Handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)

        self.register_plugin('xep_0077') # In-band Registration

    """ HANDLER RELATED """
    def start(self, event):
        self.send_presence()
        self.get_roster()

    # Basado del siguiente ejemplo
    # https://searchcode.com/file/58168360/examples/register_account.py/
    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        try:
            resp.send(now=True)
            print("Account created for", self.boundjid, '!')
        except IqError as e:
            print("Could not register account:", e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()

class Client(ClientXMPP):
    """ INIT """
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.users = []

        self.received = set()
        self.presences_received = threading.Event()
        
        # Handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

        # Notif handlers
        self.add_event_handler("changed_status", self.wait_for_presences)
        self.add_event_handler("presence_unsubscribe", self.presence_unsubscribe)
        self.add_event_handler("presence_subscribe", self.presence_subscribe)

        # Plugins
        # Registration order doesnt matter so...
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0030') # Service Disc
        self.register_plugin('xep_0077') # In-band Register
        self.register_plugin('xep_0066') # Ping
        self.register_plugin('xep_0045') # MUC

        import ssl
        self.ssl_version = ssl.PROTOCOL_TLS

    """ HANDLER RELATED """
    def start(self, event):
        self.send_presence(pshow='chat', pstatus='Hola amigos!!!! Estoy online.')
        self.get_roster()

    def message(self, msg):
        #1-to-1
        if msg['type'] in ('chat', 'normal'):
            if len(msg['body']) > 1000:
                recv = base64.decodebytes(msg['body'].encode('utf-8'))
                with open("saved.png", "wb") as fh:
                    fh.write(recv) 

                print("(PRIVATE) " + sender + ": " + "sent an image!")
            else:
                sender =  "%s@%s" % (msg['from'].user, msg['from'].domain)
                print("(PRIVATE) " + sender + ": " + msg['body'])
        #groups
        if str(msg['type']) == 'groupchat':
            sender = "%s@%s" % (msg['from'].user, msg['from'].domain)
            print("(GROUP) " + sender + ": " + msg['body'])

    """ OTHER DEFS """
    def logout(self):
        self.disconnect(wait=False)
        print("Bye! See you later")

    def unregister(self):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user

        try:
            resp.send(now=True)
            print("Account deleted ", self.boundjid, '!')
        except IqError as e:
            print("Could not delete account", e)
            self.disconnect()
        except IqTimeout:
            print("No response from server.")

        self.disconnect(wait=False)

    def login(self):
        if self.connect():
            self.process()
            print("logged in")
        else:
            print("error: couldnt log in")

    def showAllUsrs(self):
        iq = self.Iq()
        iq['type'] = 'set'
        iq['id'] = 'search_result'
        iq['to'] = 'search.redes2020.xyz'

        item = ET.fromstring("<query xmlns='jabber:iq:search'> \
                                <x xmlns='jabber:x:data' type='submit'> \
                                    <field type='hidden' var='FORM_TYPE'> \
                                        <value>jabber:iq:search</value> \
                                    </field> \
                                    <field var='Username'> \
                                        <value>1</value> \
                                    </field> \
                                    <field var='search'> \
                                        <value>*</value> \
                                    </field> \
                                </x> \
                              </query>")
        iq.append(item)
        res = iq.send()

        data = []
        temp = []
        cont = 0
        for i in res.findall('.//{jabber:x:data}value'):
            cont += 1
            txt = ''
            if cont == 2:
                temp.append(i.text)

            if cont == 4:
                cont = 0
                data.append(temp)
                temp = []

        return data

    # Lo mismo que todos los usuarios pero con parametro en username value.
    def showUsr(self, jid):
        iq = self.Iq()
        iq['type'] = 'set'
        iq['id'] = 'search_result'
        iq['to'] = 'search.redes2020.xyz'

        item = ET.fromstring("<query xmlns='jabber:iq:search'> \
                                <x xmlns='jabber:x:data' type='submit'> \
                                    <field type='hidden' var='FORM_TYPE'> \
                                        <value>jabber:iq:search</value> \
                                    </field> \
                                    <field var='Username'> \
                                        <value>1</value> \
                                    </field> \
                                    <field var='search'> \
                                        <value>" + jid + "</value> \
                                    </field> \
                                </x> \
                              </query>")
        iq.append(item)
        res = iq.send()

        data = []
        temp = []
        cont = 0
        for i in res.findall('.//{jabber:x:data}value'):
            cont += 1
            txt = ''
            if cont == 2:
                temp.append(i.text)

            if cont == 4:
                cont = 0
                data.append(temp)
                temp = []

        return data

    def sendMsg(self, jid, msg):
        self.send_message(mto=jid, mbody=msg, mtype='chat')
        print("Message sent to user " + jid + "!")

    def sendGroupMsg(self, room, msg):
        self.send_message(mto=room, mbody=msg, mtype='groupchat')
        print("Message sent to room " + room + "!")

    def joinCreateRoom(self, room, nick):
        self.plugin['xep_0045'].joinMUC(room, nick, wait=True)
        print("Room created!")

    """ NOTIFS/PRESENCE HANDLERS """
    def addUser(self, jid):
        self.send_presence_subscription(pto=jid)
        print("User added! " + jid)

    def jid_to_user(self, jid):
        jid = str(jid)
        return jid.split('@')[0]

    def presence_subscribe(self, presence):
        person = self.jid_to_user(presence['from'])
        print('-- %s added-- ' %(person))
        self.sendMsg(presence['from'], 'gracias por agregarme en tu lista, salu2!')

    def presence_unsubscribe(self, presence):
         person = self.jid_to_user(presence['from'])
         print('-- %s removed-- ' %(person))

    # Extraido de https://github.com/fritzy/SleekXMPP/blob/develop/examples/roster_browser.py
    def showRoster(self):
        try:
            self.get_roster()
        except IqError as err:
            print('Error: %s' % err.iq['error']['condition'])
        except IqTimeout:
            print('Error: Request timed out')
        self.send_presence()

        print('Waiting for presence updates...\n')
        self.presences_received.wait(5)

        print('Roster for %s' % self.boundjid.bare)
        groups = self.client_roster.groups()
        for group in groups:
            print('\n%s' % group)
            print('-' * 72)
            for jid in groups[group]:
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                if self.client_roster[jid]['name']:
                    print(' %s (%s) [%s]' % (name, jid, sub))
                else:
                    print(' %s [%s]' % (jid, sub))

                connections = self.client_roster.presence(jid)
                for res, pres in connections.items():
                    show = 'available'
                    if pres['show']:
                        show = pres['show']
                    print('   - %s (%s)' % (res, show))
                    if pres['status']:
                        print('       %s' % pres['status'])

    def wait_for_presences(self, pres):
        """
        Track how many roster entries have received presence updates.
        """
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()       

    def changePresence(self, opt, msg):
        shows = {
            "1" : "chat",
            "2" : "away",
            "3" : "xa",
            "4" : "dnd" 
        }
        
        show_txt = shows[opt]
        self.send_presence(pshow=show_txt, pstatus=msg)

    def sendFile(self, recipient, file):
        with open(file, 'rb') as img:
            file_ = base64.b64encode(img.read()).decode('utf-8')

        self.send_message(mto=recipient, mbody=file_, msubject='send_file', mtype='chat')


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
    parser.add_argument("-n", "--nick", dest="nick",
                        help="nickname")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")


    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=args.loglevel,format='%(levelname)-8s %(message)s')
    
    xmpp = Client(args.nick + domain, args.password)
    
    menu = """
        1. Registrar cuenta en el servidor.
        2. Iniciar sesion.
        15. Cerrar sesion.
    """

    logged_menu = """
        3. Eliminar cuenta.
        4. Agregar usuario a lista de contactos.
        5. Mostrar lista de contactos.
        6. Mostrar detalles de los usuarios.
        7. Mostrar detalles de un usuario.
        8. Enviar mensaje (personal).
        9. Enviar mensaje (grupal).
        10. Cambiar estado de presencia.
        11. Crear o unirse a cuarto/grupo.
        12. Enviar archivo.
        15. Cerrar sesion.
    """

    # Inicializar esto en numero cualquiera
    opt = 99
    logged = False

    while opt != "15":
        if (logged):
            opts = logged_menu
        else:
            opts = menu

        print(opts)

        opt = input("Seleccione una opcion: ")

        if opt=="1":
            reg = Register(args.nick + domain, args.password)

            if reg.connect():
                reg.process(block=True)
                print("Done")
            else:
                print("Couldn't connect to server!")
        elif opt=="2":
            xmpp.login()
            logged = True
        elif opt=="3":
            xmpp.unregister()
        elif opt=="4":
            recipient = input("Ingrese usuario a agregar: ")
            xmpp.addUser(recipient+domain)
        elif opt=="5":
            xmpp.showRoster()
        elif opt=="6":
            usrs = xmpp.showAllUsrs()

            print("CONNECTED USERS:")
            for usr in usrs:
                print("- " + usr[0])
        elif opt=="7":
            recipient = input("Ingrese usuario a buscar: ")
            usrs = xmpp.showUsr(recipient)
            
            if (usrs):
                print("USERS SEARCHED:")
                for usr in usrs:
                    print("- " + usr[0])
            else:
                print("There's no user matching your search!")
        elif opt=="8":
            recipient = input("Escriba el nombre del receptor: ")
            msg = input("Escriba el mensaje a escribir: ")
            xmpp.sendMsg(recipient+domain, msg)
        elif opt=="9":
            group = input("Escriba el nombre del grupo: ")
            msg = input("Escriba el mensaje a escribir: ")
            xmpp.sendGroupMsg(group, msg)         
        elif opt=="10":
            print("""
                Estados:
                1. chat
                2. away
                3. xa 
                4. dnd
            """)

            show = input("Ingrese un estado a asignar: ")
            msg = input("Ingrese el texto de su presencia: ")
            xmpp.changePresence(show, msg)
        elif opt=="11":
            room = input("Ingrese nombre de cuarto/grupo: ")
            nick = input("Ingrese su nickname o apodo: ")
            xmpp.joinCreateRoom(room, nick)
        elif opt=="12":
            recipient = input("Escriba el nombre del receptor: ")
            file = input("Escriba el nombre del archivo: ")
            xmpp.sendFile(recipient+domain, file)
        elif opt=="15":
            xmpp.logout()