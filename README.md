# UVG Redes - Project #2 - Existing Protocol Use
## XMPP Client
- Author: Rodrigo Zea (17058)

## Project Description
- The project's objective was to use an already existing protocol and adapt it to our own chat client.
- The chat client utilizes a CLI to interact.

## Running the project
```sh
$ git clone https://github.com/RodrigoZea/Proyecto2Redes
$ cd Proyecto2Redes
$ python -q -n nickname -p password
```

Utilized parameters are the following:
- -q/-d: This sets the console to being quiet mode (no debug log) or to debug mode (extensive verbose log).
- -n: This is the username that will be utilized for registration and logging. This is the username that will be shown to everyone else on the server.
- -p: This is the password that will be utilized for registration and logging.

# Chat features, utilization & user flow
#### Userflow
- Run python -q -n nickname -p password
- Check menu.
    - Only three options will be displayed: register, login, disconnect.
- Register an account.
- Login into your account.
- Check menu.
    - Every other chat option will be now displayed.
- Chat away!

#### Features
- Register an account.
    - Command number: 1
    - Purpose: Registers an account into the server.
    
- Login.
    - Command number: 2
    - Purpose: Logs in into your account.

- Close session.
    - Command number: 15
    - Purpose: Closes your current session on the server and stops the program.

- Delete account.
    - Command number: 3
    - Purpose: Deletes your account on the server.

- Add user.
    - Command number: 4
    - Purpose: This command lets you send a friend request to another user on the server.

- Show contact list.
    - Command number: 5
    - Purpose: This command lists all of the users who have accepted your friend request or have sent you one.
    
- Show all users.
    - Command number: 6
    - Purpose: Lists all of the users available.

- Show one user.
    - Command number: 7
    - Purpose: Lists if there's any user online given a parameter username to be searched.

- Send message.
    - Command number: 8
    - Purpose: Sends a message to another person on the server, user is prompted with the message reciever's username and the message to be displayed.

- Send group message.
    - Command number: 9
    - Purpose: Sends a message to a group (given the user is a member of the group), user is prompted with the group's name and the message to be displayed.

- Change presence.
    - Command number: 10
    - Purpose: This command lets you display a different presence message and type.

- Join or create group.
    - Command number: 11
    - Purpose: This command lets you join or create a group (in case the group doesn't exist) so you can engage in a multi user chat.

- Send an image.
    - Command number: 12
    - Purpose: This command lets you share an image with another user, given the protocol utilized is similar or the same.

# Utilized technology
- [Python](https://www.python.org/)
- [SleekXMPP (deprecated)](https://sleekxmpp.readthedocs.io/en/latest/)