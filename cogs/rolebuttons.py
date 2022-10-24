import interactions 
from interactions.ext.enhanced import extension_component
from pickledb import load as pickle_load,PickleDB
import config

NEWLINE = '\n'

class RoleButtons(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client
        self.db: PickleDB = pickle_load('role_buttons')
    
    def list_roles(self)->list[tuple[str,str]]:
        return [(key,self.db.get(key)) for key in self.db.getall()]

    @interactions.extension_command(
        name="rollen_button_erstellen",
        description="Fügt eine Rolle mit Button hinzu",
        scope=config.guilds,
        options = [
            interactions.Option(
                name="button_text",
                description="Beschreibung auf dem Button",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="role",
                description="Rolle, zum hinzufügen",
                type=interactions.OptionType.ROLE,
                required=True,
            ),
        ],
    )
    async def _rollen_button_erstellen(self,ctx:interactions.CommandContext,button_text:str,role:interactions.Role):
        self.db.set(f'{role.id}',button_text)
        roles = self.list_roles()
        await ctx.send(f'''
Button für Rolle hinzugefügt! Es sind jetzt {len(roles)} Rollen über Buttons verfügbar:
{NEWLINE.join(f'<@&{role_id}> <- {role_text}' for role_id,role_text in roles)}
            '''
            ,ephemeral=True)

    @interactions.extension_command(
        name="rollen_button_entfernen",
        description="Entfernt eine Rolle mit Button",
        scope=config.guilds,
        options = [
            interactions.Option(
                name="button_text",
                description="Beschreibung auf dem Button",
                type=interactions.OptionType.STRING,
                required=False,
            ),
            interactions.Option(
                name="role",
                description="Rolle",
                type=interactions.OptionType.ROLE,
                required=False,
            ),
        ],
    )
    async def _rollen_button_entfernen(self,ctx:interactions.CommandContext,button_text:str=None,role:interactions.Role=None):
        roles = self.list_roles()
        deleting_role = [role_id for role_id,role_text in roles if role_id==f'{role.id}' or role_text==button_text ]
        if not deleting_role:
            await ctx.send(f'Rolle konnte nicht gefunden werden. Folgende Rollen sind registriert: {NEWLINE.join(f"<@&{role_id}> <- {role_text}" for role_id,role_text in roles)}')
            return
        self.db.rem(f'{role.id}')
        await ctx.send(f'''
Button und Rolle entfernt! Es sind jetzt {len(roles)} Rollen über Buttons verfügbar:
{NEWLINE.join(f'<@&{role_id}> <- {role_text}' for role_id,role_text in roles)}
            '''
            ,ephemeral=True)

    def rollen_nachricht_bauen(self):
        roles = self.list_roles()
        text = '''
Benutze einen der Buttons, um dir eine Rolle geben zu lassen!
'''
        actionrows = interactions.spread_to_rows(
            *[
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label=role_text,
                    custom_id=f'role_button_{role_id}'
                )
                for role_id,role_text in roles
            ],
            interactions.Button(
                style=interactions.ButtonStyle.DANGER,
                label='Aktualisieren',
                custom_id=f'aktualisieren'
            )

        )
        return {'content':text,'components':actionrows}

    @extension_component("aktualisieren")
    async def aktualisieren(self,ctx:interactions.ComponentContext):
        await ctx.message.edit(**self.rollen_nachricht_bauen())

    @extension_component("role_button_", startswith=True)
    async def role_button(self,ctx:interactions.ComponentContext):
        role_id = ctx.custom_id.split('_')[-1]
        role_text = [text for id,text in self.list_roles() if id==role_id]
        if role_text:
            await ctx.send(f'Rolle vergeben <@&{role_id}> ',ephemeral=True)
        else:
            await ctx.send(f'Für den Button {role_text} ist **keine** Rolle mehr hinterlegt. Aktualisiere die Buttonnachricht')
    
def setup(client):
  RoleButtons(client)