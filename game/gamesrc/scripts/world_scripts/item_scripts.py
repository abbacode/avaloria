from game.gamesrc.scripts.basescripts import Script


class StateLightSourceOn(Script):
    """
    Script used to keep track of a light source item being on or off.
    """
    def at_script_creation(self):
        
