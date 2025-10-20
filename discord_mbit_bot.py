import os


@bot.event
async def on_ready():
global DB_CONN
# initialize DB
DB_CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
init_db(DB_CONN)
print(f"Bot ready. Logged in as {bot.user} (id: {bot.user.id})")
try:
synced = await bot.tree.sync()
print(f"Synced {len(synced)} command(s)")
except Exception as e:
print(f"Could not sync commands: {e}")




# Slash command to post the M-Bit message in the current channel
@bot.tree.command(name="post_mbit", description="Poste die M-Bit Nachricht mit Button (nur einmal oder bei Bedarf).")
@app_commands.checks.has_permissions(manage_guild=True)
async def post_mbit(interaction: discord.Interaction):
"""Post a message with the button. Requires Manage Guild permission by the caller."""
rem = remaining_count(DB_CONN)
embed = discord.Embed(title="M‑Bit – Zufallsnummern", description="Klicke auf den Button, um eine zufällige vierstellige Nummer zu erhalten. Jeder User darf nur einmal klicken; jede Nummer nur einmal vergeben.")
embed.set_footer(text=f"Verfügbare Nummeren: {rem}")
view = MBitView()
await interaction.response.send_message(embed=embed, view=view)




# Text command to post the same embed+button in the channel where the command was used
@bot.command(name="create")
@commands.has_permissions(manage_guild=True)
async def create(ctx: commands.Context):
"""Post the M-Bit embed with button in the current channel. Requires Manage Guild."""
rem = remaining_count(DB_CONN)
embed = discord.Embed(title="M‑Bit – Zufallsnummern", description="Klicke auf den Button, um eine zufällige vierstellige Nummer zu erhalten. Jeder User darf nur einmal klicken; jede Nummer nur einmal vergeben.")
embed.set_footer(text=f"Verfügbare Nummeren: {rem}")
view = MBitView()
await ctx.send(embed=embed, view=view)




# A helper command for admins to inspect one user's number
@bot.tree.command(name="get_number_of", description="Zeige, welche Nummer ein Nutzer hat. (Admin/Manage Guild)")
@app_commands.describe(user="Der Benutzer, dessen Nummer du sehen möchtest")
@app_commands.checks.has_permissions(manage_guild=True)
async def get_number_of(interaction: discord.Interaction, user: discord.Member):
num = get_user_number(DB_CONN, user.id)
if num:
await interaction.response.send_message(f"{user.mention} hat die Nummer **{num}**.")
else:
await interaction.response.send_message(f"{user.mention} hat noch keine Nummer.")




# Error handler for permission check
@post_mbit.error
@get_number_of.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
if isinstance(error, app_commands.errors.MissingPermissions):
await interaction.response.send_message("Du hast nicht die notwendigen Berechtigungen, um diesen Befehl zu benutzen.", ephemeral=True)
else:
await interaction.response.send_message(f"Fehler: {error}", ephemeral=True)




# Error handler for the text command
@create.error
async def create_error(ctx: commands.Context, error: Exception):
if isinstance(error, commands.MissingPermissions):
await ctx.send("Du hast nicht die notwendigen Berechtigungen, um diesen Befehl zu benutzen.", delete_after=8)
else:
await ctx.send(f"Fehler: {error}", delete_after=8)




# Run the bot
if __name__ == "__main__":
if not TOKEN or TOKEN.startswith("YOUR_"):
print("ERROR: Please set the DISCORD_TOKEN environment variable to your bot token before running.")
else:
bot.run(TOKEN)
