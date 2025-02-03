`1.0.0`
-------

- **From 17.0 version**
**Replaced message viewing. You can view your own and all messages separately.**
The "My Messages" tab has added the ability to view messages from channels where either the recipient or sender is the user who is currently viewing this list. The "All Messages" tab contains all messages related to messengers, but the tab will not be available to regular operators. Both "My Messages" and "All Messages" will be available to the admin.

**Operators menu.**
The system automatically adds one operator instead of all to a newly created channel, the algorithm is the same as in live chat. You can view which operator has how many channels. You can also quickly enter the channel. If the channel does not have an operator, then any operator present in this bot can become an operator.

**Ability to write your own code.**
If the user writes his own code, then it will not be erased with messenger updates, and the bot will have a message that the codes are different. Now the bot has two developer codes and user codes. Developer code cannot be edited, but user code can.

- **Only on 18.0 version**
Added a new setting in "Messengers" that allows user-operators to change the operator of their channel, and if disabled then only admins in any channels can do this.

**The chatter now does not show methods of sending messages that are not available to the user.**
For example, Mark Demo has a correspondence with the user Bob in Telegram and Mitchell only has Bob's Viber. Then Mitchell the Admin will not be able to see the check mark in the chatter that he can send messages via Telegram, he will only see it via Viber.

Now when sending from the chatter, the link at the end of the message will not lead to a document but to a specific message

`1.0.1`
-------
Fix bug with module base_accounting_kit. Optimize orm call request by adding fields that needed

`1.0.2`
-------
Fix bug with "Cannot read properties of undefined (reading 'channel_ids')" when record of res.partner hasn't user_id