# Poll sender bot
This bot was made to send polls to the group chat of our university group.
This poll is used to document the attendance.

### How it works
In the morning on work days the `send_poll.py` script is started 
by the crontab and the poll is being sent. 

There are also commands that are processed 
by handlers in `main.py` module. These commands are used
to get help section, delete a poll from the chat, or to send one out of schedule.
