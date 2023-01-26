# Poll sender bot
This bot was made to send polls to the group chat of our school class.
This poll is used to figure out whether students are going to attend classes 
the next day or not.

### How it works
Every day in the evening the `send_poll.py` script is started 
by the crontab and the poll is being send. 

There are also commands that are processed 
by handlers in `main.py` module. This commands are used
to get help section, delete a poll from the chat, or to send one out of schedule.
