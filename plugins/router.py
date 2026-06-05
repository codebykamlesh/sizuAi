"""
Sizu AI Bot — Global Command Router
"""
import difflib
from pyrogram import Client, filters
from pyrogram.types import Message
from core.commands import registry, CommandPermissionError, CommandValidationError
from utils.logger import setup_logger

log = setup_logger("sizu.router")


@Client.on_message(filters.regex(r"^/[a-zA-Z0-9_]+") & ~filters.bot, group=-1)
async def command_router(client: Client, message: Message):
    # Parse the command text
    text = (message.text or message.caption or "").strip()
    if not text.startswith("/"):
        return

    # Split command from arguments
    parts = text.split(None, 1)
    cmd_part = parts[0]
    
    # Extract command name and strip bot username if present (e.g. /start@SizuAIBot -> start)
    cmd_name = cmd_part[1:].split("@", 1)[0].lower()
    
    # Lookup in registry
    cmd = registry.get_command(cmd_name)
    user_id = message.from_user.id if message.from_user else "N/A"
    chat_id = message.chat.id
    
    if not cmd:
        # Unknown command. Fuzzy match suggestions.
        # Exclude hidden commands from suggestions list
        all_cmds = [name for name, c in registry.commands.items() if not c.is_hidden]
        close_matches = difflib.get_close_matches(cmd_name, all_cmds, n=1, cutoff=0.7)
        
        # Log failure
        log.warning(f"Command Failure | User: {user_id} | Chat: {chat_id} | Command: {text} | Reason: Unknown command")
        
        if close_matches:
            await message.reply(
                f"❌ Unknown command.\n\n"
                f"Did you mean:\n/{close_matches[0]}"
            )
        else:
            await message.reply(
                f"❌ Unknown command: /{cmd_name}\n\n"
                f"Try:\n/help\n\nor type / to view available commands."
            )
        
        message.stop_propagation()
        return

    # Split arguments
    args_str = parts[1].strip() if len(parts) > 1 else ""
    args = args_str.split() if args_str else []
    
    # Inject arguments into message.command for compatibility with original code
    message.command = [cmd_name] + args
    
    try:
        # 1. Permission checks
        await registry.check_permissions(client, message, cmd)
        
        # 2. Argument validation (number of arguments)
        if len(args) < cmd.required_args:
            raise CommandValidationError("Missing required argument.")
            
        # 3. Execute handler
        await cmd.handler(client, message)
        
    except CommandPermissionError as pe:
        log.warning(f"Command Failure | User: {user_id} | Chat: {chat_id} | Command: {text} | Reason: Permission denied (Required: {cmd.permissions})")
        await message.reply(
            f"❌ You don't have permission to use this command.\n\n"
            f"Required:\n{cmd.permissions}"
        )
    except CommandValidationError as ve:
        log.warning(f"Command Failure | User: {user_id} | Chat: {chat_id} | Command: {text} | Reason: Validation error ({str(ve)})")
        
        usage = f"Syntax:\n`{cmd.syntax}`"
        example = f"Example:\n`{cmd.examples[0]}`" if cmd.examples else ""
        
        reply = f"❌ {str(ve)}\n\n{usage}"
        if example:
            reply += f"\n\n{example}"
        await message.reply(reply)
    except Exception as e:
        log.error(f"Command Failure | User: {user_id} | Chat: {chat_id} | Command: {text} | Reason: Unhandled exception ({str(e)})", exc_info=True)
        await message.reply(f"❌ An error occurred while executing this command: {str(e)}")
        
    message.stop_propagation()
