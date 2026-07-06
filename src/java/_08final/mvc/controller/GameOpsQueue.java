package _08final.mvc.controller;

import _08final.mvc.model.Movable;
import java.util.concurrent.LinkedBlockingDeque;



/**
 * Effectively a Queue that enqueues and dequeues Game Operations (add/remove).
 * enqueue() may be called by main and animation threads simultaneously, therefore we
 * compose a data structure from the java.util.concurrent package rather than exposing
 * the entire Deque API through inheritance.
 */
public class GameOpsQueue {

    private final LinkedBlockingDeque<GameOp> deque = new LinkedBlockingDeque<>();

    public void enqueue(Movable mov, GameOp.Action action) {
        deque.addLast(new GameOp(mov, action));
    }

    public GameOp dequeue() {
        return deque.removeFirst();
    }

    public boolean isEmpty() {
        return deque.isEmpty();
    }
}
