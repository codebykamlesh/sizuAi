"""
Sizu AI Bot — Centralized Command Registry
"""
import difflib
from pyrogram import Client
from pyrogram.types import Message, BotCommand
from pyrogram.enums import ChatMemberStatus, ChatType
from config import Config

class CommandPermissionError(Exception):
    """Raised when user lacks permission to execute a command."""
    def __init__(self, required_role: str):
        super().__init__(f"You don't have permission to use this command. Required: {required_role}")
        self.required_role = required_role

class CommandValidationError(Exception):
    """Raised when command argument validation fails."""
    pass

class CommandInfo:
    def __init__(self, name, description, category, syntax, examples, permissions="User", required_args=0, aliases=None, is_hidden=False, handler=None):
        self.name = name
        self.description = description
        self.category = category
        self.syntax = syntax
        self.examples = examples or []
        self.permissions = permissions  # "User", "Admin", "Sudo", "Owner"
        self.required_args = required_args
        self.aliases = aliases or []
        self.is_hidden = is_hidden
        self.handler = handler

class CommandRegistry:
    def __init__(self):
        self.commands = {}

    def register(self, name, description, category, syntax, examples=None, permissions="User", required_args=0, aliases=None, is_hidden=False):
        """Decorator to register a command in the central registry."""
        def decorator(func):
            cmd = CommandInfo(
                name=name,
                description=description,
                category=category,
                syntax=syntax,
                examples=examples or [],
                permissions=permissions,
                required_args=required_args,
                aliases=aliases or [],
                is_hidden=is_hidden,
                handler=func
            )
            self.commands[name] = cmd
            for alias in cmd.aliases:
                self.commands[alias] = cmd
            return func
        return decorator

    def get_command(self, name: str) -> CommandInfo:
        """Retrieve command info by name or alias (case-insensitive)."""
        return self.commands.get(name.lower())

    async def check_permissions(self, client: Client, message: Message, command: CommandInfo) -> bool:
        """
        Verify if the message sender has permissions to execute the command.
        Raises CommandPermissionError if check fails.
        """
        if not message.from_user:
            raise CommandPermissionError(command.permissions)
            
        user_id = message.from_user.id
        perm = command.permissions
        
        # Owner check (always passes all checks)
        if user_id == Config.OWNER_ID:
            return True
            
        if perm == "Owner":
            raise CommandPermissionError("Owner")
            
        if perm == "Sudo":
            if user_id not in Config.SUDO_USERS:
                raise CommandPermissionError("Sudo")
            return True
            
        if perm == "Admin":
            # Check owner/sudo first
            if user_id in Config.SUDO_USERS:
                return True
            # Check group admin status
            if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                try:
                    member = await client.get_chat_member(message.chat.id, user_id)
                    if member.status not in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
                        raise CommandPermissionError("Admin")
                except Exception:
                    raise CommandPermissionError("Admin")
            else:
                raise CommandPermissionError("Admin")
                
        return True

    def get_pyrogram_commands(self, admin: bool = False) -> list[BotCommand]:
        """
        Get all commands for registering with Telegram Bot API menu.
        Filters out hidden commands and restricts admin commands based on scope.
        """
        cmds = []
        seen = set()
        for name, cmd in self.commands.items():
            if cmd.is_hidden or name in seen:
                continue
            seen.add(name)
            # Skip admin-only commands if requested for standard scope
            if cmd.permissions in ("Admin", "Sudo", "Owner") and not admin:
                continue
            cmds.append(BotCommand(command=cmd.name, description=cmd.description))
        return cmds

    def get_all_command_names(self) -> list[str]:
        """Return flat list of all registered commands and aliases (used for message exclusion filters)."""
        return list(self.commands.keys())

    def get_help_text(self, command_name: str = None, is_admin: bool = False) -> str:
        """
        Generate dynamic help text.
        If command_name is specified, returns detailed command usage.
        Otherwise, returns a categorized help menu.
        """
        if command_name:
            cmd = self.get_command(command_name)
            if not cmd or (cmd.is_hidden and not is_admin):
                return f"❌ Command not found: /{command_name}"
            
            # Smart help detail
            lines = [
                f"**Command:** `/{cmd.name}`",
                "",
                f"**Description:**\n{cmd.description}",
                "",
                f"**Syntax:**\n`{cmd.syntax}`"
            ]
            if cmd.examples:
                lines.append("")
                lines.append(f"**Example:**\n`{cmd.examples[0]}`")
            if cmd.permissions != "User":
                lines.append("")
                lines.append(f"**Required Permission:** `{cmd.permissions}`")
            return "\n".join(lines)

        # Categorized global help menu
        lines = [
            "╭──────────────────────────────╮",
            "│     ✨  **SIZU HELP MENU**  ✨   │",
            "├──────────────────────────────┤",
            "│  💬 **Chat**                     │",
            "│  Just text me — I'll reply!   │",
            "│                              │"
        ]
        
        category_icons = {
            "General": "📊",
            "AI": "🧠",
            "Games": "🎮",
            "Utilities": "🛠",
            "Fun": "🎭",
            "Admin": "🔑",
        }
        
        # Organize visible commands by category
        categories = {}
        for name, cmd in self.commands.items():
            if cmd.is_hidden or name != cmd.name:  # Skip aliases/hidden
                continue
            # Skip admin categories/commands if caller is not admin
            if cmd.permissions in ("Admin", "Sudo", "Owner") and not is_admin:
                continue
            categories.setdefault(cmd.category, []).append(cmd.name)

        # Standard category sort order
        sort_order = ["General", "AI", "Games", "Utilities", "Fun", "Admin"]
        for cat in sort_order:
            if cat not in categories:
                continue
            cmds = sorted(categories[cat])
            icon = category_icons.get(cat, "🔹")
            lines.append(f"│  {icon} **{cat}**")
            
            visible_cmds = [f"/{c}" for c in cmds]
            for i in range(0, len(visible_cmds), 3):
                chunk = visible_cmds[i:i+3]
                lines.append(f"│  " + "  ".join(chunk))
            lines.append("│                              │")
            
        if lines[-1] == "│                              │":
            lines.pop()
        lines.append("╰──────────────────────────────╯")
        lines.append("")
        lines.append("_Powered by DeepSeek · Built with ❤️_")
        return "\n".join(lines)

# Registry instance singleton
registry = CommandRegistry()
register_command = registry.register

def get_help_text(command_name: str = None, is_admin: bool = False) -> str:
    """Wrapper function to get help text from the registry."""
    return registry.get_help_text(command_name, is_admin)

def get_all_command_names() -> list[str]:
    """Wrapper function to get all command names from the registry."""
    return registry.get_all_command_names()

def get_pyrogram_commands(admin: bool = False) -> list[BotCommand]:
    """Wrapper function to get bot command suggestions from the registry."""
    return registry.get_pyrogram_commands(admin)
