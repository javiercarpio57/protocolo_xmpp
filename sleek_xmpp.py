import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
import sleekxmpp
from prettytable import PrettyTable

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Usuario():
    def __init__(self, user, status, show, subscription, online):
        self.user = user
        self.show = show
        self.status = status
        self.subscription = subscription
        self.online = online

    def set_states(self, status, show):
        self.status = status
        self.show = show

    def set_online(self, online):
        self.online = online

    def get_username(self):
        return self.user

    def get_usuario(self):
        return [self.user, self.status, self.show, self.online, self.subscription]

class Cliente(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.timeout = 45
        self.my_jid = jid.lower()
        self.usuarios = []

        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('message', self.message)
        self.add_event_handler('changed_status', self.on_presence)
        self.add_event_handler("presence_unsubscribe", self.presence_unsubscribe)
        self.add_event_handler("presence_subscribe", self.presence_subscribe)
        self.add_event_handler("got_offline", self.got_offline)
        self.add_event_handler("got_online", self.got_online)
        
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)

        import ssl
        self.ssl_version = ssl.PROTOCOL_TLS
        
    def presence_unsubscribe(self, presence):
        person = self.jid_to_user(presence['from'])

        print(bcolors.FAIL + '-- %s te eliminó -- ' %(person) + bcolors.ENDC)
        for i in range(len(self.usuarios)):
            if self.usuarios[i].get_username() == person:
                self.usuarios.pop(i)
                break

    def presence_subscribe(self, presence):
        person = self.jid_to_user(presence['from'])

        print(bcolors.OKGREEN + '-- %s te agregó -- ' %(person) + bcolors.ENDC)
        self.SendMessageTo(presence['from'], 'Gracias por agregarme :)')

        u = Usuario(person, '---', '---', 'both', 'No')
        self.usuarios.append(u)

    def got_offline(self, presence):        
        if self.jid not in str(presence['from']):
            u = self.jid_to_user(str(presence['from']))
            print(bcolors.FAIL + '-- %s está en offline -- ' %(u) + bcolors.ENDC)

            for i in self.usuarios:
                if i.get_username() == u:
                    i.set_online('No')
                    break

    def got_online(self, presence):
        # print('ONLINE:', presence)
        isGroup = self.IsGroup(str(presence['from']))
        if isGroup:
            nick = str(presence['from']).split('@')[1].split('/')[1]
            groupname = str(presence['from']).split('@')[0]
            print(bcolors.OKGREEN + '-- %s está en %s -- ' %(nick, groupname) + bcolors.ENDC)
        else:
            if self.jid not in str(presence['from']):
                u = self.jid_to_user(str(presence['from']))
                print(bcolors.OKGREEN + '-- %s está en online -- ' %(u) + bcolors.ENDC)

                for i in self.usuarios:
                    if i.get_username() == u:
                        i.set_online('Sí')
                        break

    def session_start(self, event):
        self.send_presence(pshow='chat', pstatus='Listo para chatear, amigos :)')
        roster = self.get_roster()
        
        for r in roster['roster']['items'].keys():
            subs = str(roster['roster']['items'][r]['subscription'])

            user = self.jid_to_user(str(r))

            if user != self.jid_to_user(self.my_jid):
                show = '---'
                status = 'unavailable'
                
                u = Usuario(user, status, show, subs, 'No')
                self.usuarios.append(u)

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(bcolors.WARNING + '\t==> [PRIVATELY: %(from)s] %(body)s' % (msg) + bcolors.ENDC)
        if str(msg['type']) == 'groupchat':
            print(bcolors.WARNING + '\t--> (%(from)s): %(body)s' %(msg) + bcolors.ENDC)

    def on_presence(self, presence):
        user = str(presence['from'])
        user = self.jid_to_user(user)

        if user != self.jid_to_user(self.my_jid):
            if str(presence['type']) == 'unavailable':
                status = str(presence['type'])
                show = '---'
            else:
                if str(presence['status']):
                    status = str(presence['status'])
                else:
                    status = '---'
                if str(presence['show']):
                    show = str(presence['show'])
                else:
                    show = '---'

            encontrado = False
            index = 0
            for i in self.usuarios:
                if user in i.get_usuario():
                    encontrado = True
                    break
                index += 1

            if encontrado:
                self.usuarios[index].set_states(status, show)
            else:
                u = Usuario(user, status, show)
                self.usuarios.append(u)

    def IsGroup(self, from_jid):
        if 'conference' in from_jid.split('@')[1]:
            return True
        else:
            return False

    def SendMessageTo(self, jid, message):
        self.send_message(mto=jid, mbody=message, mtype='chat')

    def SendMessageRoom(self, room, message):
        self.send_message(mto=room, mbody=message, mtype='groupchat')

    def Login(self):
        success = False
        if self.connect():
            self.process()
            success = True
            print(bcolors.OKGREEN + 'Login exitoso' + bcolors.ENDC)
        else:
            print(bcolors.FAIL + 'Ha ocurrido un error' + bcolors.ENDC)

        return success

    def AddUser(self, jid):
        self.send_presence_subscription(pto=jid)

    def GetUser(self, username):
        us = []
        for i in self.usuarios:
            if username.lower() == i.get_username():
                us.append(i.get_usuario())
        return us            

    def GetUsers(self):

        for i in self.roster.keys():
            for j in self.roster[i].keys():
                print('--', self.roster[i][j], '--')

        us = []
        for i in self.usuarios:
            us.append(i.get_usuario())

        return us

    def jid_to_user(self, jid):
        jid = str(jid)
        return jid.split('@')[0]

    def RemoveUser(self, jid):
        self.del_roster_item(jid)

        person = self.jid_to_user(jid)
        for i in range(len(self.usuarios)):
            if self.usuarios[i].get_username() == person:
                self.usuarios.pop(i)
                break

    def ChangeStatus(self, show, status):
        self.send_presence(pshow=show, pstatus=status)

    def JoinOrCreateRoom(self, room, nickname):
        self.plugin['xep_0045'].joinMUC(room, nickname, wait=True)
        

class RegisterBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('register', self.register)

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration

    def start(self, event):
        self.send_presence()
        self.get_roster()

        self.disconnect()

    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            print(bcolors.OKGREEN + 'Cuenta creada para ' + self.boundjid + '!' + bcolors.ENDC)
        except IqError as e:
            print(bcolors.FAIL + 'No se ha podido registrar cuenta' + bcolors.ENDC)
            self.disconnect()
        except IqTimeout:
            print(bcolors.FAIL + 'Sin respuesta del server...' + bcolors.ENDC)
            self.disconnect()

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(levelname)-8s %(message)s')

    domain = '@redes2020.xyz'
    show_state = {
        '1': 'chat',
        '2': 'away',
        '3': 'xa',
        '4': 'dnd'
    }

    menu1 = '''
============================
0. Salir
1. Registrar nueva cuenta
2. Iniciar sesion
============================
'''

    menu2 = '''
====================================
0. Cerrar sesión
1. Mostrar listado de usuarios
2. Agregar un usuario a contactos
3. Mostrar detalles de contacto
4. Enviar mensaje privado
5. Enviar mensaje grupal
6. Definir mensaje de presencia
7. Eliminar usuario
8. Cambiar de estado
9. Crear o unirte a sala
====================================
'''

    opcion = ''
    hasLogin = False

    while opcion != '0':
        if not hasLogin:
            opcion = input(menu1)

            if opcion == '1':
                username = input('Ingrese su username: ')
                password = input('Ingrese su password: ')

                regi = RegisterBot(username + domain, password)

                if regi.connect():
                    regi.process(block=True)
                else:
                    print(bcolors.FAIL + 'Conexión falló...' + bcolors.ENDC)
            elif opcion == '2':
                username = input('Ingrese su username: ')
                password = input('Ingrese su password: ')

                xmpp = Cliente(username + domain, password)
                if xmpp.Login():
                    hasLogin = True
            elif opcion == '0':
                print(bcolors.OKBLUE + 'Espero vuelva pronto' + bcolors.ENDC)
            else:
                print(bcolors.FAIL + 'Opción incorrecta' + bcolors.ENDC)
        else:
            opcion = input(menu2)

            if opcion == '1':
                users = xmpp.GetUsers()
                t = PrettyTable(['User', 'Status', 'Show', 'Online', 'Subscription'])
                for i in users:
                    t.add_row(i)
                print(t)

            elif opcion == '2':
                user = input('Ingrese el jid: ')
                xmpp.AddUser(user)

            elif opcion == '3':
                u = input('Ingresa el username para obtener información: ')
                users = xmpp.GetUser(u)
                t = PrettyTable(['User', 'Status', 'Show', 'Online', 'Subscription'])
                for i in users:
                    t.add_row(i)
                print(t)

            elif opcion == '4':
                to = input('¿A quién va el mensaje? ')
                msg = input('Ingresa el mensaje: ')
                xmpp.SendMessageTo(to, msg)

            elif opcion == '5':
                room = input('Ingrese el room para enviar mensaje: ')
                msg = input('Ingrese su mensaje: ')

                xmpp.SendMessageRoom(room, msg)

            elif opcion == '7':
                remove_to = input('¿A quién deseas eliminar? ')
                xmpp.RemoveUser(remove_to)

            elif opcion == '8':
                show_error = True
                while show_error:
                    show = input('Ingresa tu show:\n 1. chat\n 2. away\n 3. xa\n 4. dnd\n')
                    if show in show_state.keys():
                        show_error = False
                status = input('Ingrese su nuevo estado: ')
                xmpp.ChangeStatus(show_state[show], status)
            
            elif opcion == '9':
                room = input('Ingrese room: ')
                nickname = input('Ingresa tu nickname: ')

                xmpp.JoinOrCreateRoom(room, nickname)
            elif opcion == '0':
                xmpp.disconnect()
                opcion = ''
                hasLogin = False