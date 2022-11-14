g3state() {
    // NEW GAME
    if (
        this.gameStarted == false
        )
    {
        string = "New Game"
        gamestate = 1
        return this.setGamestate(string, gamestate)
    }
    // NO POKEMON
    else if (            
        this.mapper.properties.player.name.bytes > 0 &&
        this.mapper.properties.player.teamCount.value == 0 &&
        this.gameStarted == false
        ) 
    {
        string = "No Pokemon"
        gamestate = 2
        return this.setGamestate(string, gamestate)
    }      
    // OVERWORLD
    else if (
        this.mapper.properties.player.name.bytes > 0 &&
        this.mapper.properties.player.teamCount.value > 0 &&
        this.gameStarted == true
        ||
        this.mapper.properties.battle.turnInfo.battleOutcome.bytes > 0 && 
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value == 0
    ) 
    {
        string = "Overworld"
        gamestate = 3
        return this.setGamestate(string, gamestate)
    }
    // POST-RESET
    else if (
        this.mapper.properties.battle.turnInfo.battleOutcome.bytes == 0 && 
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value == 0 &&
        this.mapper.properties?.player?.teamCount > 0 &&
        this.gameStarted == true 
    ) 
    {
        string = "Post-Reset"
        gamestate = 9
        return this.setGamestate(string, gamestate)
    }
    //  TO BATTLE
    else if (
        this.mapper.properties.battle.turnInfo.battleDialogue.bytes != 18 &&
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value > 0 &&
        this.currentGameStateNew == "New Game"
        ||
        this.mapper.properties.battle.turnInfo.battleDialogue.bytes != 18 &&
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value > 0 &&
        this.currentGameStateNew == "Overworld"
        ||
        this.mapper.properties.battle.turnInfo.battleDialogue.bytes != 18 &&
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value > 0 &&
        this.currentGameStateNew == "To Battle"
        ||
        this.mapper.properties.battle.turnInfo.battleDialogue.bytes != 18 &&
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value > 0 &&
        this.currentGameStateNew == "Post-Reset"
    ) 
    {
        string = "To Battle"
        gamestate = 4
        return this.setGamestate(string, gamestate)
    }
    // BATTLE
    else if (
        this.mapper.properties.battle.turnInfo.battleDialogue.bytes == 18 ||
        this.mapper.properties.battle.turnInfo.battleOutcome.bytes == 0 && 
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value > 0 &&
        this.currentGameStateNew == "Battle"
    ) 
    {
        string = "Battle"
        gamestate = 5
        this.gameStarted = true
        return this.setGamestate(string, gamestate)
    }
    // DOUBLE-BATTLE
    else if (
        this.mapper.properties.battle.turnInfo.battleDialogue.bytes == 18 ||
        this.mapper.properties.battle.turnInfo.battleOutcome.bytes == 0 && 
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value > 0 &&
        this.currentGameStateNew == "Battle"
    ) 
    {
        string = "Double-Battle"
        gamestate = 6
        return this.setGamestate(string, gamestate)
    } 
    // FROM BATTLE
    else if (
        this.mapper.properties.battle.turnInfo.battleOutcome.bytes > 0 && 
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value > 0
    ) 
    {

        string = "From Battle"
        gamestate = 7
        return this.setGamestate(string, gamestate)
    }
    // RESET
    else if (
        this.mapper.properties.battle.turnInfo.battleOutcome.bytes == 0 && 
        this.mapper.properties.battle.turnInfo.battleBackgroundTiles.value == 0 &&
        this.mapper.properties?.player?.teamCount == 0 &&
        this.gameStarted == true
    ) 
    {
        string = "Reset"
        gamestate = 8
        return this.setGamestate(string, gamestate)
    }
    // ERROR
    else {
        string = "Error"
        gamestate = 10
        return this.setGamestate(string, gamestate)
    }
}