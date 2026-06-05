"""
Notes plugin — save, retrieve, list, and delete notes per chat.
"""
from pyrogram import Client, filters
from pyrogram.types import Message

from database.mongo import db
from utils.logger import setup_logger

log = setup_logger("sizu.notes")


from core.commands import register_command, CommandValidationError
from utils.logger import setup_logger

log = setup_logger("sizu.notes")


@register_command(
    name="note",
    description="Save a note. Specify content or reply to a message.",
    category="Utilities",
    syntax="/note <name> <content>",
    examples=["/note rules No spam allowed."],
    required_args=1
)
async def cmd_save_note(client: Client, message: Message):
    """
    Save a note. Usage: /note <name> <text>
    Or reply to a message: /note <name>
    """
    args = message.command[1:]
    name = args[0].lower()

    if len(args) >= 2:
        text = " ".join(args[1:])
    elif message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    else:
        raise CommandValidationError("Give me the note content! Either after the name, or reply to a message.")

    await db.save_note(message.chat.id, name, text)
    await message.reply(f"📝 Note **{name}** saved! Get it with `/notes {name}`")


@register_command(
    name="notes",
    description="List all notes saved in this chat, or retrieve a specific one by name.",
    category="Utilities",
    syntax="/notes [name]",
    examples=["/notes", "/notes rules"]
)
async def cmd_get_notes(client: Client, message: Message):
    """
    Get a specific note or list all notes.
    Usage: /notes <name> or /notes
    """
    args = message.command[1:]
    chat_id = message.chat.id

    if args:
        name = args[0].lower()
        note = await db.get_note(chat_id, name)
        if note:
            await message.reply(
                f"📌 **{name}**\n\n{note['text']}"
            )
        else:
            await message.reply(f"No note called **{name}** found. Use `/notes` to list all.")
    else:
        note_names = await db.list_notes(chat_id)
        if not note_names:
            await message.reply("No notes saved here yet! Use `/note <name> <text>` to create one.")
        else:
            names_str = "\n".join(f"• `{n}`" for n in sorted(note_names))
            await message.reply(
                f"📋 **Saved Notes**\n\n{names_str}\n\n"
                f"└ Use `/notes <name>` to get a note"
            )


@register_command(
    name="delnote",
    description="Delete a saved note.",
    category="Utilities",
    syntax="/delnote <name>",
    examples=["/delnote rules"],
    required_args=1
)
async def cmd_delete_note(client: Client, message: Message):
    """Delete a note. Usage: /delnote <name>"""
    args = message.command[1:]
    name = args[0].lower()
    deleted = await db.delete_note(message.chat.id, name)
    if deleted:
        await message.reply(f"🗑️ Note **{name}** deleted.")
    else:
        await message.reply(f"No note called **{name}** found.")
