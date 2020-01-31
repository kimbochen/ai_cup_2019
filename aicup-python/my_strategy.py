import model


class MyStrategy:
    def __init__(self):
        pass

    def get_action(self, unit, game, debug):
        def distance_sqr(a, b):
            return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

        # Find the nearest enemy unit
        nearest_enemy = min(
            filter(lambda u: u.player_id != unit.player_id, game.units),
            key=lambda u: distance_sqr(u.position, unit.position),
            default=None)

        # Find the best weapon: the nearest one
        best_weapon = min(
            filter(lambda box: isinstance(box.item, model.Item.Weapon),
                   game.loot_boxes),
            key=lambda box: distance_sqr(box.position, unit.position),
            default=None)

        # Calculate the position in the next tick
        if unit.weapon is None and best_weapon is not None:
            target_pos = best_weapon.position
        elif nearest_enemy is not None:
            target_pos = nearest_enemy.position
        else:
            target_pos = unit.position

        '''
        if unit.weapon is None and best_weapon is not None:
            target_pos = best_weapon.position
        elif nearest_enemy is not None:
            target_pos = nearest_enemy.position
        '''

        debug.draw(model.CustomData.Log("Target pos: {}".format(target_pos)))

        # Calculate the aiming direction
        aim = model.Vec2Double(0, 0)
        if nearest_enemy is not None:
            aim = model.Vec2Double(
                nearest_enemy.position.x - unit.position.x,
                nearest_enemy.position.y - unit.position.y)

        # Decide whether the unit should jump
        jump = target_pos.y > unit.position.y
        if target_pos.x > unit.position.x and game.level.tiles[int(unit.position.x + 1)][int(unit.position.y)] == model.Tile.WALL:
            jump = True
        if target_pos.x < unit.position.x and game.level.tiles[int(unit.position.x - 1)][int(unit.position.y)] == model.Tile.WALL:
            jump = True

        # Decide whether the unit should shoot
        vector_len = (aim.x ** 2 + aim.y ** 2) ** 0.5
        unit_aim = model.Vec2Double(aim.x / vector_len, aim.y / vector_len)

        start_x = min(unit.position.x, nearest_enemy.position.x)
        end_x = max(unit.position.x, nearest_enemy.position.x)
        start_y = min(unit.position.y, nearest_enemy.position.y)
        end_y = max(unit.position.y, nearest_enemy.position.y)
        shoot = True

        cur_x, cur_y = unit.position.x, unit.position.y
        while start_x <= cur_x <= end_x and start_y <= cur_y <= end_y:
            if game.level.tiles[int(cur_x)][int(cur_y)] != model.Tile.EMPTY:
                shoot = False
                break
            else:
                cur_x += unit_aim.x
                cur_y += unit_aim.y

        unit_action = model.UnitAction(
            velocity=target_pos.x - unit.position.x,
            jump=jump,
            jump_down=not jump,
            aim=aim,
            shoot=shoot,
            reload=False,
            swap_weapon=False,
            plant_mine=False)

        return unit_action
