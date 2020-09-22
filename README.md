# XMPP protocol

## Installation
Use the **requirements.txt** file to install python dependencies, as follow:
```
pip install -r requirements.txt
```
Then, run the program:
```
python xmpp_protocol.py
```

## Usage
### Login and Register
To register a new user, select option 1 and fill the username, password, name and email fields.
Then, you can login with the created account.

### Show all users/contacts
After doing login, choose option 1.

### Add user to contacts
Choose option 2, and write the user's jid.

### Show user's info
Choose option 3, and write the user's jid that you want to get extra info.

### Send private message to user/contact
Choose option 4, and fill the receiver and message content fields.

### Rooms
Choose option 5, and to join or create a new room select 1, and write the room's jid. Otherwise, select 2 to send messages to groups that you've joined previously.

## Presence stanza
In other words, changing your status. Choose option 6 and fill the show and status fields to change your status.

### Send files
Choose option 8, it'll ask you to browse a file, and in this case, only images (jpg, jpeg, png).

### Notifications
You'll receive the following notifications:
- When a contact added you
- When a contact deleted you
- When a contact got online
- When a contact got offline

### Other functionalities
#### Remove a contact
Choose option 7, and write the user's jid that you want to delete from your contact list.

#### Unregister
Choose option 9, and your account will be removed from the server.