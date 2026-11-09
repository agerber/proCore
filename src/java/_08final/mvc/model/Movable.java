package _08final.mvc.model;

import java.awt.*;
import java.util.LinkedList;


/* NOTE Movable is NOT the Facade design pattern, although it is often mislabeled as such. A Facade is a single class
 that offers a simplified front door to a complicated subsystem (see SoundLoader and ImageLoader for the real
 Facades in this code base). Movable is the model's *contract*: the seven operations the engine needs from anything
 that lives in the game space. The controller and view program to this interface and never to Falcon or Asteroid,
 which is why a class such as Star can implement Movable directly without extending Sprite.
 */
public interface Movable {

	enum Team {FRIEND, FOE, FLOATER, DEBRIS}

	//for the game to move and draw movable objects. See the GamePanel class.
	void move();
	void draw(Graphics g);

	//for collision detection
	Point getCenter();
	int getRadius();
	Team getTeam();



	/* NOTE addToGame() and removeFromGame() are lifecycle callbacks, also called HOOK METHODS, and they are NOT the
	 Observer pattern (nothing subscribes to them; Game simply calls them on exactly one object when it drains the
	 ops queue). Sprite supplies the default behavior (add/remove self from the list); subclasses override the hook
	 to add a side effect at that moment in the object's life: Bullet plays a sound on add, Asteroid spawns smaller
	 asteroids and awards points on remove, Nuke refuses to be removed before it expires. Hooks are the variable
	 steps of the TEMPLATE METHOD that processGameOpsQueue() implements; see Sprite for the pattern annotation.
	 */

	//this is your opportunity to add sounds or perform other side effects.
	//The 'list' parameter will be one of the following: movFriends, movFoes, movDebris, movFloaters.
	//See processGameOpsQueue() of Game class
	void addToGame(LinkedList<Movable> list);

	void removeFromGame(LinkedList<Movable> list);


} //end Movable
