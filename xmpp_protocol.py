import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
from sleekxmpp.plugins.xep_0096 import stanza, File
from sleekxmpp.exceptions import IqError, IqTimeout
import sleekxmpp
from prettytable import PrettyTable

import subprocess
from tkinter import filedialog
import os

# import magic
import filetype
import base64
from datetime import datetime
import time

# Print with colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Get file's path
def my_file():
    image_formats= [("JPEG", "*.jpg"), ("JPG", "*.jpeg"), ("PNG", "*.png")]
    filename = filedialog.askopenfilename( initialdir="C:/", title="select file", filetypes=image_formats)

    return filename

class Usuario():
    # Initialize User variables
    def __init__(self, user, status, show, subscription, online):
        self.user = user
        self.show = show
        self.status = status
        self.subscription = subscription
        self.online = online

    # Set state of User
    def set_states(self, status, show):
        self.status = status
        self.show = show

    # Change online in on/off
    def set_online(self, online):
        self.online = online

    # Get User username
    def get_username(self):
        return self.user

    # Get all info of User
    def get_usuario(self):
        return [self.user, self.status, self.show, self.online, self.subscription]

class Cliente(ClientXMPP):

    # Initialize Cliente variables
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.timeout = 45
        self.my_jid = jid.lower()
        self.usuarios = []
        self.rooms = {}
        self.contador_rooms = 1

        # Manage all events
        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('message', self.message)
        self.add_event_handler('changed_status', self.on_presence)
        self.add_event_handler("presence_unsubscribe", self.presence_unsubscribe)
        self.add_event_handler("presence_subscribe", self.presence_subscribe)
        self.add_event_handler("got_offline", self.got_offline)
        self.add_event_handler("got_online", self.got_online)
        
        # Register all plug-ins
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0096') # File transfer

        import ssl
        self.ssl_version = ssl.PROTOCOL_TLS
        
    # Trigger when someone unsubscribe
    def presence_unsubscribe(self, presence):
        person = self.jid_to_user(presence['from'])

        print(bcolors.FAIL + '-- %s te eliminó -- ' %(person) + bcolors.ENDC)
        for i in range(len(self.usuarios)):
            if self.usuarios[i].get_username() == person:
                self.usuarios.pop(i)
                break

    # Trigger when someone subscribe
    def presence_subscribe(self, presence):
        person = self.jid_to_user(presence['from'])

        print(bcolors.OKGREEN + '-- %s te agregó -- ' %(person) + bcolors.ENDC)
        self.SendMessageTo(presence['from'], 'Gracias por agregarme :)')

        u = Usuario(person, '---', '---', 'both', 'No')
        self.usuarios.append(u)

    # Trigger when someone got offline
    def got_offline(self, presence):        
        if self.boundjid.bare not in str(presence['from']):
            u = self.jid_to_user(str(presence['from']))
            print(bcolors.FAIL + '-- %s está en offline -- ' %(u) + bcolors.ENDC)

            for i in self.usuarios:
                if i.get_username() == u:
                    i.set_online('No')
                    break

    # Trigger when someone got online
    def got_online(self, presence):
        isGroup = self.IsGroup(str(presence['from']))
        if isGroup:
            nick = str(presence['from']).split('@')[1].split('/')[1]
            groupname = str(presence['from']).split('@')[0]
            print(bcolors.OKGREEN + '-- %s está en %s -- ' %(nick, groupname) + bcolors.ENDC)
        else:
            if self.boundjid.bare not in str(presence['from']):
                u = self.jid_to_user(str(presence['from']))
                print(bcolors.OKGREEN + '-- %s está en online -- ' %(u) + bcolors.ENDC)

                for i in self.usuarios:
                    if i.get_username() == u:
                        i.set_online('Sí')
                        break

    # Trigger when User wants to connect to server
    def session_start(self, event):
        self.send_presence(pshow='chat', pstatus='Quiero dormirrr')
        roster = self.get_roster()
        
        for r in roster['roster']['items'].keys():
            subs = str(roster['roster']['items'][r]['subscription'])

            user = self.jid_to_user(str(r))

            if user != self.jid_to_user(self.my_jid):
                show = '---'
                status = 'unavailable'
                
                u = Usuario(user, status, show, subs, 'No')
                self.usuarios.append(u)

    # Trigger when someone sends a private chat and groupchat
    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            if msg['subject'] == 'send_file' or len(msg['body']) > 500:
                img_body = msg['body']
                file_ = img_body.encode('utf-8')
                file_ = base64.decodebytes(file_)
                with open("redes_" + str(int(time.time())) + ".png", "wb") as f:
                    f.write(file_)
                print(bcolors.WARNING + '\t==> %(from)s te envió un archivo...' % (msg) + bcolors.ENDC)
            else:
                print(bcolors.WARNING + '\t==> [PRIVATELY: %(from)s] %(body)s' % (msg) + bcolors.ENDC)
        if str(msg['type']) == 'groupchat':
            print(bcolors.WARNING + '\t--> (%(from)s): %(body)s' %(msg) + bcolors.ENDC)

    # Trigger when someone changed status
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

    # Check if jid has 'conference'
    def IsGroup(self, from_jid):
        if 'conference' in from_jid.split('@')[1]:
            return True
        else:
            return False

    # Send message to jid
    def SendMessageTo(self, jid, message):
        self.send_message(mto=jid, mbody=message, mtype='chat')

    # Send message to room
    def SendMessageRoom(self, room, message):
        self.send_message(mto=room, mbody=message, mtype='groupchat')

    # Let user to login
    def Login(self):
        success = False
        if self.connect():
            self.process()
            success = True
            print(bcolors.OKGREEN + 'Login exitoso' + bcolors.ENDC)
        else:
            print(bcolors.FAIL + 'Ha ocurrido un error' + bcolors.ENDC)

        return success

    # Send subscription presence to jid
    def AddUser(self, jid):
        self.send_presence_subscription(pto=jid)

    # Send file to jid
    def SendFile(self, path, to):
        with open(path, 'rb') as img:
            file_ = base64.b64encode(img.read()).decode('utf-8')

        self.send_message(mto=to, mbody=file_, msubject='send_file', mtype='chat')
        
    # Get a user info
    def GetUser(self, username):
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
                                        <value>" + username + "</value> \
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
            if i.text == None:
                txt = '--'
            else:
                txt = i.text

            temp.append(txt)
            if cont == 4:
                cont = 0
                data.append(temp)
                temp = []

        us = []
        for i in self.usuarios:
            if username.lower() == i.get_username():
                us.append(i.get_usuario())
        return us, data

    # Get all users info
    def GetUsers(self):

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
        try:
            res = iq.send()
            data = []
            temp = []
            cont = 0
            for i in res.findall('.//{jabber:x:data}value'):
                cont += 1
                txt = ''
                if i.text == None:
                    txt = '--'
                else:
                    txt = i.text

                temp.append(txt)
                if cont == 4:
                    cont = 0
                    data.append(temp)
                    temp = []

            us = []
            for i in self.usuarios:
                us.append(i.get_usuario())

            return us, data
        except IqTimeout:
            print('Sin respuesta del server')
            return [], []
        

    # Transform jid to only username
    def jid_to_user(self, jid):
        jid = str(jid)
        return jid.split('@')[0]

    # Remove a user from contact list
    def RemoveUser(self, jid):
        self.del_roster_item(jid)

        person = self.jid_to_user(jid)
        for i in range(len(self.usuarios)):
            if self.usuarios[i].get_username() == person:
                self.usuarios.pop(i)
                break

    # Change status of user
    def ChangeStatus(self, show, status):
        self.send_presence(pshow=show, pstatus=status)

    # Let user to join or create a room
    def JoinOrCreateRoom(self, room, nickname, creating):
        self.plugin['xep_0045'].joinMUC(room, nickname, wait=True)

        if creating:
            self.plugin['xep_0045'].setAffiliation(room, self.boundjid.full, affiliation='owner')
            self.plugin['xep_0045'].configureRoom(room, ifrom=self.boundjid.full)

        self.rooms[str(self.contador_rooms)] = room
        self.contador_rooms += 1

    # Remove user from server
    def Unregister(self):
        iq = self.make_iq_set(ito='redes2020.xyz', ifrom=self.boundjid.user)
        item = ET.fromstring("<query xmlns='jabber:iq:register'> \
                                <remove/> \
                              </query>")
        iq.append(item)

        try:
            res = iq.send()
            if res['type'] == 'result':
                print(bcolors.OKGREEN + 'Cuenta eliminada' + bcolors.ENDC)
        except IqTimeout:
            print('Sin respuesta del server')

class RegisterUser(sleekxmpp.ClientXMPP):
    # Initialize variables
    def __init__(self, jid, password, name, email):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.name = name
        self.email = email

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('register', self.register)

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration

    # Trigger when user wants to connect
    def start(self, event):
        self.send_presence()
        self.get_roster()

        self.disconnect()

    # Used to register a new user in server
    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        resp['register']['name'] = self.name
        resp['register']['email'] = self.email

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
5. Funcionalidad de rooms
6. Definir mensaje de presencia (cambiar estado)
7. Eliminar a un usuario
8. Enviar un archivo
9. Eliminar mi cuenta
====================================
'''

    opcion = ''
    hasLogin = False

    while opcion != '0':
        if not hasLogin:
            opcion = input(menu1)

            if opcion == '1':
                username = input('Ingrese tu username: ')
                password = input('Ingrese tu password: ')
                name = input('Ingresa tu nombre: ')
                email = input('Ingresa tu email: ')

                regi = RegisterUser(username + domain, password, name, email)

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
                users, server_users = xmpp.GetUsers()
                t = PrettyTable(['User', 'Status', 'Show', 'Online', 'Subscription'])
                for i in users:
                    t.add_row(i)
                print(t)

                t2 = PrettyTable(['Email', 'JID', 'Username', 'Name'])
                for i in server_users:
                    t2.add_row(i)
                print(t2)

            elif opcion == '2':
                user = input('Ingrese el jid: ')
                xmpp.AddUser(user)

            elif opcion == '3':
                u = input('Ingresa el username para obtener información: ')
                users, server_user = xmpp.GetUser(u)
                t = PrettyTable(['User', 'Status', 'Show', 'Online', 'Subscription'])
                for i in users:
                    t.add_row(i)
                print(t)

                t2 = PrettyTable(['Email', 'JID', 'Username', 'Name'])
                for i in server_user:
                    t2.add_row(i)
                print(t2)

            elif opcion == '4':
                to = input('¿A quién va el mensaje? ')
                msg = input('Ingresa el mensaje: ')
                xmpp.SendMessageTo(to, msg)

            elif opcion == '5':
                opcion_menu = input('1. Crear sala\n2. Unirte a sala\n3. Enviar mensaje a sala\n')
                if opcion_menu == '1':
                    room = input('Ingrese room: ')
                    nickname = input('Ingresa tu nickname: ')

                    xmpp.JoinOrCreateRoom(room, nickname, True)
                elif opcion_menu == '2':
                    room = input('Ingrese room: ')
                    nickname = input('Ingresa tu nickname: ')

                    xmpp.JoinOrCreateRoom(room, nickname, False)

                elif opcion_menu == '3':
                    for index, r in xmpp.rooms.items():
                        print(str(index) + '. ' + r)
                    room = input('Ingrese el room para enviar mensaje (numero): ')
                    if room in xmpp.rooms.keys():
                        msg = input('Ingrese su mensaje: ')
                        xmpp.SendMessageRoom(xmpp.rooms[room], msg)
                    else:
                        print('Opcion incorrecta')
                else:
                    print('Opcion incorrecta')

            elif opcion == '6':
                show_error = True
                while show_error:
                    show = input('Ingresa tu show:\n 1. chat\n 2. away\n 3. xa\n 4. dnd\n')
                    if show in show_state.keys():
                        show_error = False
                status = input('Ingrese su nuevo estado: ')
                xmpp.ChangeStatus(show_state[show], status)

            elif opcion == '7':
                remove_to = input('¿A quién deseas eliminar? ')
                xmpp.RemoveUser(remove_to)
            
            elif opcion == '8':
                path = my_file()
                if path:
                    to_person = input('Ingresa el jid para enviar el archivo: ')
                    xmpp.SendFile(path, to_person)

            elif opcion == '9':
                xmpp.Unregister()
                opcion = '0'

            if opcion == '0':
                xmpp.disconnect()
                opcion = ''
                hasLogin = False