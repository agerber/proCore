package _08final.mvc.controller;

import _08final.mvc.model.Movable;

/**
 The GameOp (short for Game Operation) simply associates a movable with an action. Once
 the GameOpsQueue is processed it will add/remove movables from their appropriate list
 in the CommandCenter depending on the movable's team.
 */
public record GameOp(Movable movable, Action action) {

    //this could also be a boolean, but we want to be explicit about what we're doing
    public enum Action {
        ADD, REMOVE
    }

}
