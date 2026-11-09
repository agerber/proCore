package _08final.mvc.controller;


import java.awt.*;
import _08final.mvc.model.*;
import lombok.Data;

import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Optional;

//The CommandCenter is a singleton that manages the state of the game.
//the lombok @Data gives us automatic getters and setters on all members
@Data
public class CommandCenter {


	private  int numFalcons;
	private  int level;
	private  long score;
	private  boolean paused;
	private  boolean themeMusic;
	private boolean radarToggle; //to toggle on/off the radar
	//this value is used to count the number of frames (full animation cycles) in the game
	private long frame;

	//the falcon is located in the movFriends list, but since we use this reference a lot, we keep track of it in a
	//separate reference. Use final to ensure that the falcon ref always points to the single falcon object on heap.
	//Lombok will not provide setter methods on final members
	private final Falcon falcon  = new Falcon();
	private final Radar radar = new Radar();

	//inner record associating a universe name with its dimension (as a multiple of the game screen)
	record Universe(String name, Dimension dimension) { }

	private final Universe[] universes =  new Universe[] {
			new Universe("FREE FLY", new Dimension(1, 1)),
			new Universe("CENTER", new Dimension(1, 1)),
			new Universe("BIG", new Dimension(2, 2)),
			new Universe("HORIZONTAL", new Dimension(3, 1)),
			new Universe("VERTICAL", new Dimension(1, 3)),
			new Universe("DARK", new Dimension(4, 4))

	};
	/* NOTE These four lists are NOT the Composite design pattern, although they are often mislabeled as such.
	 In Composite, the container is itself a Component (a LinkedList<Movable> would have to implement Movable so that
	 a group of sprites could be moved and drawn as one sprite). These are plain polymorphic collections: each list
	 holds heterogeneous Movables (Falcon, Bullet, Asteroid, Star ...) and the engine calls move()/draw() through the
	 interface without knowing the concrete class. That is interface polymorphism (Chapter 17), not a GoF pattern.
	 */
	private final LinkedList<Movable> movDebris = new LinkedList<>();
	private final LinkedList<Movable> movFriends = new LinkedList<>();
	private final LinkedList<Movable> movFoes = new LinkedList<>();
	private final LinkedList<Movable> movFloaters = new LinkedList<>();

	private final GameOpsQueue opsQueue = new GameOpsQueue();



	/* TODO PATTERN 1 of 10: SINGLETON. CommandCenter is the one object that holds the game's state (score, level,
	 the team lists, the ops queue), so the class guarantees a single instance: the constructor is private, the sole
	 instance lives in a private static field, and getInstance() is the global access point that creates it lazily on
	 first use. Cost of the pattern: global state is hard to test and the lazy check below is not thread-safe (two
	 threads could both see null); an enum singleton or a static holder class fixes that. See Chapter 43.
	 */
	private static CommandCenter instance = null;

	// Constructor made private
	private CommandCenter() {}

    //this class maintains game state - make this a singleton.
	public static CommandCenter getInstance(){
		if (instance == null){
			instance = new CommandCenter();
		}
		return instance;
	}


	public void initGame(){

		clearAll();
		generateStarField();
		setLevel(0);
		setRadarToggle(true);
		setScore(0);
		setPaused(false);
		//set to one greater than number of falcons lives in your game as decrementFalconNumAndSpawn() also decrements
		setNumFalcons(4);
		falcon.decrementFalconNumAndSpawn();
		//The following two objects are initialized at start game. All other sprites should be enqueued during gameplay
		opsQueue.enqueue(falcon, GameOp.Action.ADD);
		opsQueue.enqueue(radar, GameOp.Action.ADD);
		//theme music
		SoundLoader.playSound("dr_loop.wav");
		setThemeMusic(true);


	}


	private void generateStarField(){

		int count = 100;
		while (count-- > 0){
			opsQueue.enqueue(new Star(), GameOp.Action.ADD);
		}
	}

	public void incrementFrame(){
		frame = frame < Long.MAX_VALUE ? frame + 1 : 0;
	}

	private void clearAll(){
		movDebris.clear();
		movFriends.clear();
		movFoes.clear();
		movFloaters.clear();
	}

	public void killAllFoes(){
		for (Movable movFoe : movFoes)
			opsQueue.enqueue(movFoe, GameOp.Action.REMOVE);
	}

	public boolean isGameOver() {		//if the number of falcons is zero, then game over
		return numFalcons < 1;
	}

	public Dimension getUniDim(){
		Optional<Universe> universe = optUni();
		return universe.isEmpty() ? new Dimension(1,1) : universe.get().dimension();

	}

	public String getUniName(){
		Optional<Universe> universe = optUni();
		return universe.isEmpty() ? "" : universe.get().name();
	}

	public boolean isFalconPositionFixed(){
		Optional<Universe> universe = optUni();
		return universe.isEmpty() ? true : (!universe.get().name().equalsIgnoreCase("FREE FLY"));
	}
	private Optional<Universe> optUni() {
		if (getLevel() == 0) {
			return Optional.empty();
		}
		int index = (getLevel() - 1) % universes.length;
		return Optional.of(universes[index]);
	}

}
