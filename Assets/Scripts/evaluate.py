import math
import UnityEngine as ue
import random

playerPrefab = ue.Resources.Load("Prefabs/Mario")
player_container = ue.GameObject.Find("Players")

properties = ue.GameObject.Find("Game Manager").GetComponent("GeneticAlgorithm")

flag_position = ue.GameObject.Find("FlagPole").transform.position

def newPlayer():
  return ue.GameObject.Instantiate(
    playerPrefab, 
    ue.Vector3(2, 2, 0), 
    ue.Quaternion(0, 0, 0, 0), 
    player_container.transform).GetComponent("Player")
  

# Fitness from distance, death, and collisions
# F(x) = 1/(DistanceToFlagPole + IsDead + CollisionCount)
def fitness(players):
  for player in players:
    distance = ue.Vector3.Distance(flag_position, player.transform.position)
    collision_penalty = player.collisionCount
    death_penalty = 9999 if player.isDead else 0
    player.fitness = 1 / (distance + death_penalty + collision_penalty) * 1000
    if player.win:
      player.fitness *= 1000
    if player.fitness > properties.bestFitness:
      properties.bestFitness = player.fitness
  return players

# Selects the best players
def selection(players):
  temp = [(player, player.fitness) for player in players]

  temp = sorted(temp, key=lambda player: player[1], reverse=True)

  players = [player for player, _ in temp]

  if properties.isDone:
    return players

  for index, player in enumerate(players):
    if (index >= properties.selectionCount):
      ue.Object.Destroy(player.gameObject)

  return players[:properties.selectionCount]

# Creates offspring
def crossover(players):
  offspring = []

  for _ in range(int(math.ceil(properties.populationSize - properties.selectionCount)/2)):
    parent1 = random.choice(players)
    parent2 = random.choice(players)

    child1 = newPlayer()
    child2 = newPlayer()

    split = random.randint(properties.moveSavedCount + 1, properties.moveCount)
    
    for i in range(properties.moveSavedCount + 1, split):
      child1.moves[i] = parent1.moves[i]
      child2.moves[i] = parent2.moves[i]
    
    for i in range(split, properties.moveSavedCount):
      child1.moves[i] = parent2.moves[i]
      child2.moves[i] = parent1.moves[i]

    offspring.append(child1)
    offspring.append(child2)
  
  new_players = []
  for player in players:
    new_player = newPlayer()
    new_player.moves = player.moves
    new_players.append(new_player)
    ue.Object.Destroy(player.gameObject)
  
  new_players.extend(offspring)

  return new_players

def mutation(players):
  for player in players:
    for idx in range(properties.moveSavedCount + 1, properties.moveSavedCount):
      if random.uniform(0.0, 1.0) <= properties.mutationRate:
        player.moves[idx] = properties.MOVESLIST[random.randint(0, 2)]
  return players

# Increases the moveCount for the new generation
def increase_moves():
  properties.moveSavedCount = properties.moveCount
  properties.moveCount += properties.moveIncreaseAmount
  players = fitness(properties.players)
  best_player = selection(players)[0]
  properties.moveSaved = best_player.moves
  for player in players:
    ue.Object.Destroy(player.gameObject)
  properties.players = [newPlayer() for _ in range(properties.populationSize)]
  
# Run the evaluation
def genetic_algorithm():
  players = fitness(properties.players)
  players = selection(players)
  players = crossover(players)
  players = mutation(players)
  properties.players = players

if __name__ == "__main__":
  properties.currentGeneration += 1
  if properties.isDone or properties.currentGeneration > properties.generationMax:
    players = fitness(properties.players)
    properties.moveSaved = selection(players)[0].moves
    properties.moveSavedCount = properties.moveCount;
  else:
    if properties.currentGeneration >= 10 and (properties.currentGeneration - 10) % properties.generationPerMoveIncrease == 0:
      increase_moves()
    else:
      genetic_algorithm()
    
    properties.finishedCount = 0
    properties.isRunning = True