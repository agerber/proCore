package _08final.mvc.controller;

import _08final.mvc.model.*;
import _08final.mvc.view.GamePanel;


import java.awt.*;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.util.LinkedList;
import java.util.Random;


// ===============================================
// == This Game class is the CONTROLLER
// ===============================================
/* TODO PATTERN 2 of 10: MODEL-VIEW-CONTROLLER (an architectural pattern). The three packages are the three roles.
   MODEL (mvc.model): Movable, Sprite and its subclasses hold position, velocity, team and know how to move() and
   draw() themselves, but know nothing about keyboards or windows. VIEW (mvc.view): GameFrame and GamePanel own the
   window and the off-screen image; GamePanel.update() asks every model object to draw itself. CONTROLLER
   (mvc.controller): Game translates keystrokes into model changes, runs the frame loop, detects collisions and
   spawns sprites; CommandCenter holds the model's aggregate state. The separation is what lets the same models be
   rendered by a different view (the Python port renders the same design with PIL and tkinter).
 */

public class Game implements Runnable, KeyListener {

    // ===============================================
    // FIELDS
    // ===============================================

    //the dimension of the game-screen. Computed once at class-load from the environment so it is
    //effectively-final and available before any Sprite (which reads Game.DIM) is constructed.
    public static final Dimension DIM = setDimFromEnv();



    private final GamePanel gamePanel;
    //this is used throughout many classes.
    public static final Random R = new Random();

    public final static int ANIMATION_DELAY = 40; // milliseconds between frames

    public final static int FRAMES_PER_SECOND = 1000 / ANIMATION_DELAY;

    //points awarded for clearing a level (scaled by the level number)
    public static final long LEVEL_CLEAR_BONUS = 10_000L;

    private final Thread animationThread;


    //key-codes
    private static final int
            PAUSE = 80, // p key
            QUIT = 81, // q key
            LEFT = 37, // rotate left; left arrow
            RIGHT = 39, // rotate right; right arrow
            UP = 38, // thrust; up arrow
            START = 83, // s key
            FIRE = 32, // space key
            MUTE = 77, // m-key mute
            NUKE = 70, // f-key
            KILL = 86, // v-key
            RADAR = 65; // a-key


    // ===============================================
    // ==CONSTRUCTOR
    // ===============================================

    public Game() {
        gamePanel = new GamePanel(DIM);
        /* TODO PATTERN 4 of 10: OBSERVER. Swing's listener model is the Observer pattern. GamePanel is the subject
           (it owns the keyboard focus); Game is the observer; addKeyListener() is the subscribe step; and whenever a
           key event occurs, Swing calls back keyPressed()/keyReleased() below on the Event Dispatch Thread. The
           panel never references Game by type, only through the KeyListener interface, so any number of listeners
           could be added without changing the panel. Note that the lifecycle callbacks addToGame()/removeFromGame()
           in Movable are NOT Observer: nobody subscribes to them, they are hook methods (see Movable and Sprite).
         */
        gamePanel.addKeyListener(this); //Game object implements KeyListener
        //fire up the animation thread
        animationThread = new Thread(this); // pass the animation thread a runnable object, the Game object
        //set as daemon so as not to block the main thread from exiting
        animationThread.setDaemon(true);
        animationThread.start();



    }

    // ===============================================
    // ==METHODS
    // ===============================================

    public static void main(String[] args) {


        //typical Swing application start; we pass EventQueue a Runnable object.
        EventQueue.invokeLater(Game::new);
    }

    /*
    in the Environmental Variables of the runtime configuration:
    WIDTH=980;HEIGHT=600 or something like this.
     */
    private static Dimension setDimFromEnv(){

        Dimension dimension;
        try {
            String width = System.getenv("WIDTH");
            String height = System.getenv("HEIGHT");
            dimension = new Dimension(Integer.parseInt(width), Integer.parseInt(height));
        } catch (NumberFormatException e) {
            //some default value
            dimension =  new Dimension(1200, 700);
        }
        return dimension;
    }

    /* TODO PATTERN 5 of 10: GAME LOOP (from Robert Nystrom's Game Programming Patterns). run() is a loop that is
       decoupled from user input: every ~40 ms it (1) renders a frame by asking each Movable to move() and draw()
       itself (GamePanel.update), (2) resolves collisions, levels and spawns, (3) drains the ops queue, and (4)
       sleeps for whatever remains of the frame budget, so the game runs at the same speed on a fast or a slow
       machine. Input arrives asynchronously on the Event Dispatch Thread and is applied here, never the other way
       round. The loop runs on its own daemon thread so Swing keeps repainting and listening.
     */
    // Game implements runnable, and must have run method
    @Override
    public void run() {

        // lower animation thread's priority, thereby yielding to the 'Event Dispatch Thread'
        // thread which listens to keystrokes
        animationThread.setPriority(Thread.MIN_PRIORITY);

        // and get the current time
        long startTime = System.currentTimeMillis();

        // this thread animates the scene
        while (Thread.currentThread() == animationThread) {


            //this call will cause all movables to move() and draw() themselves every ~40ms
            // see GamePanel class for details.
            //getGraphics() can return null if the panel is not (yet) displayable, e.g. minimized;
            //guard against it and dispose the context we obtained to avoid leaking native resources.
            Graphics graphics = gamePanel.getGraphics();
            if (graphics != null) {
                try {
                    gamePanel.update(graphics);
                } finally {
                    graphics.dispose();
                }
            }

            checkCollisions();
            checkNewLevel();
            checkFloaters();
            //this method will execute addToGame() and removeFromGame() callbacks on Movable objects
            processGameOpsQueue();
            //keep track of the frame for development purposes
            CommandCenter.getInstance().incrementFrame();

            // surround the sleep() in a try/catch block
            // this simply controls delay time between
            // the frames of the animation
            try {
                // The total amount of time is guaranteed to be at least ANIMATION_DELAY long.  If processing (update)
                // between frames takes longer than ANIMATION_DELAY, then the difference between startTime -
                // System.currentTimeMillis() will be negative, then zero will be the sleep time
                startTime += ANIMATION_DELAY;

                Thread.sleep(Math.max(0,
                        startTime - System.currentTimeMillis()));
            } catch (InterruptedException e) {
                // do nothing (bury the exception), and just continue, e.g. skip this frame -- no big deal
            }
        } // end while
    } // end run

    private void checkFloaters() {
        if (CommandCenter.getInstance().isGameOver()) return;
        spawnShieldFloater();
        spawnNukeFloater();
    }

    /*
    TODO PATTERN 3 of 10: COMMAND. A GameOp is a request turned into an object: it names a receiver (the Movable) and
    an action (ADD or REMOVE) and nothing else. checkCollisions() creates GameOps while it iterates the team lists;
    processGameOpsQueue() executes them afterwards, when no iteration is in flight. Separating the *request* from
    its *execution* is the whole point of Command, and here it buys two things: (1) safety, because mutating a
    LinkedList while iterating it throws ConcurrentModificationException, and (2) thread-safety, because the Event
    Dispatch Thread (keyPressed, e.g. firing a Bullet) and the animation thread both enqueue onto the same
    LinkedBlockingDeque and only the animation thread drains it (a producer-consumer hand-off). See GameOp,
    GameOpsQueue, and Chapter 43.
     */

    private void checkCollisions() {

        CommandCenter cc = CommandCenter.getInstance();
        //This has order-of-growth of O(FOES * FRIENDS)
        Point pntFriendCenter, pntFoeCenter;
        int radFriend, radFoe;
        for (Movable movFriend : cc.getMovFriends()) {
            for (Movable movFoe : cc.getMovFoes()) {

                pntFriendCenter = movFriend.getCenter();
                pntFoeCenter = movFoe.getCenter();
                radFriend = movFriend.getRadius();
                radFoe = movFoe.getRadius();

                //detect collision
                if (pntFriendCenter.distance(pntFoeCenter) < (radFriend + radFoe)) {
                    //enqueue the friend
                    cc.getOpsQueue().enqueue(movFriend, GameOp.Action.REMOVE);
                    //enqueue the foe
                    cc.getOpsQueue().enqueue(movFoe, GameOp.Action.REMOVE);
                }
            }//end inner for
        }//end outer for

        //check for collisions between falcon and floaters. Order of growth of O(FLOATERS)
        Point pntFalCenter = cc.getFalcon().getCenter();
        int radFalcon = cc.getFalcon().getRadius();

        Point pntFloaterCenter;
        int radFloater;
        for (Movable movFloater : cc.getMovFloaters()) {
            pntFloaterCenter = movFloater.getCenter();
            radFloater = movFloater.getRadius();
            //detect collision
            if (pntFalCenter.distance(pntFloaterCenter) < (radFalcon + radFloater)) {
                //enqueue the floater
                cc.getOpsQueue().enqueue(movFloater, GameOp.Action.REMOVE);
            }//end if
        }//end for

    }//end meth


    //This method adds and removes movables to/from their respective linked-lists.
    private void processGameOpsQueue() {

        //deferred mutation: these operations are done AFTER we have completed our collision detection to avoid
        // mutating the movable linkedlists while iterating them above.
        CommandCenter cc = CommandCenter.getInstance();
        while (!cc.getOpsQueue().isEmpty()) {

            GameOp gameOp = cc.getOpsQueue().dequeue();

            //given team, determine which linked-list this object will be added-to or removed-from
            Movable mov = gameOp.movable();
            LinkedList<Movable> list = switch (mov.getTeam()) {
                case FOE -> cc.getMovFoes();
                case FRIEND -> cc.getMovFriends();
                case FLOATER -> cc.getMovFloaters();
                case DEBRIS -> cc.getMovDebris();
            };

            //pass the appropriate linked-list from above
            //this block will execute the addToGame() or removeFromGame() callbacks in the Movable models.
            if (gameOp.action() == GameOp.Action.ADD)
                mov.addToGame(list);
            else //REMOVE
                mov.removeFromGame(list);

        }//end while
    }


    private void spawnShieldFloater() {
        CommandCenter cc = CommandCenter.getInstance();
        if (cc.isGameOver() || cc.isPaused()) return;

        if (cc.getFrame() % ShieldFloater.SPAWN_SHIELD_FLOATER == 0) {
            cc.getOpsQueue().enqueue(new ShieldFloater(), GameOp.Action.ADD);
        }
    }

    private void spawnNukeFloater() {
        CommandCenter cc = CommandCenter.getInstance();
        if (cc.isGameOver() || cc.isPaused()) return;

        if (cc.getFrame() % NukeFloater.SPAWN_NUKE_FLOATER == 0) {
            cc.getOpsQueue().enqueue(new NukeFloater(), GameOp.Action.ADD);
        }
    }


    //this method spawns new Large (0) Asteroids
    private void spawnBigAsteroids(int num) {

        CommandCenter cc = CommandCenter.getInstance();
        while (num-- > 0) {
            //Asteroids with size of zero are big
            cc.getOpsQueue().enqueue(new Asteroid(0), GameOp.Action.ADD);

        }
    }





    private boolean isLevelClear() {
        //if there are no more Asteroids on the screen
        boolean asteroidFree = true;
        for (Movable movFoe : CommandCenter.getInstance().getMovFoes()) {
            if (movFoe instanceof Asteroid) {
                asteroidFree = false;
                break;
            }
        }
        return asteroidFree;
    }

    private void checkNewLevel() {

        //short-circuit if level not yet cleared
        if (!isLevelClear()) return;

        CommandCenter cc = CommandCenter.getInstance();
        //currentLevel will be zero at beginning of game
        int level = cc.getLevel();
        //award some points for having cleared the previous level
        cc.setScore(cc.getScore() + (LEVEL_CLEAR_BONUS * level));

        //center the falcon at each level-clear
        cc.getFalcon().setCenter(new Point(Game.DIM.width / 2, Game.DIM.height / 2));

        //bump the level up
        cc.setLevel(++level);
        //spawn some big new asteroids
        spawnBigAsteroids(level);
        //make falcon invincible momentarily in case new asteroids spawn on top of him, and give player
        //time to adjust to new universe and new asteroids in game space.
        cc.getFalcon().setShield(Falcon.INITIAL_SPAWN_TIME);
        //show "Level: [X] UNIVERSE" in middle of screen
        cc.getFalcon().setShowLevel(Falcon.INITIAL_SPAWN_TIME);


    }

    // ===============================================
    // KEYLISTENER METHODS
    // ===============================================

    @Override
    public void keyPressed(KeyEvent e) {
        CommandCenter cc = CommandCenter.getInstance();
        Falcon falcon = cc.getFalcon();
        int keyCode = e.getKeyCode();
        switch (keyCode) {
            case FIRE:
                cc.getOpsQueue().enqueue(new Bullet(falcon), GameOp.Action.ADD);
                break;
            case NUKE:
                cc.getOpsQueue().enqueue(new Nuke(falcon), GameOp.Action.ADD);
                break;
            case UP:
                falcon.setThrusting(true);
                SoundLoader.playSound("whitenoise_loop.wav");
                break;
            case LEFT:
                falcon.setTurnState(Falcon.TurnState.LEFT);
                break;
            case RIGHT:
                falcon.setTurnState(Falcon.TurnState.RIGHT);
                break;
            default:
                break;
        }

    }

    @Override
    public void keyReleased(KeyEvent e) {
        CommandCenter cc = CommandCenter.getInstance();
        Falcon falcon = cc.getFalcon();
        int keyCode = e.getKeyCode();
        //show the key-code in the console
        System.out.println(keyCode);

        if (keyCode == START && cc.isGameOver()) {
            cc.initGame();
            return;
        }

        switch (keyCode) {

            //releasing either the LEFT or RIGHT arrow key will set the TurnState to IDLE
            case LEFT:
            case RIGHT:
                falcon.setTurnState(Falcon.TurnState.IDLE);
                break;
            case UP:
                falcon.setThrusting(false);
                SoundLoader.stopSound("whitenoise_loop.wav");
                break;
            case PAUSE:
                cc.setPaused(!cc.isPaused());
                break;
            case KILL:
                // cheat to speed game play during development
                cc.killAllFoes();
                break;
            case QUIT:
                System.exit(0);
                break;
            case RADAR:
                //toggle the boolean switch
                cc.setRadarToggle(!cc.isRadarToggle());
                break;
            case MUTE:
                //if music is currently playing, then stop
                if (cc.isThemeMusic()) {
                    SoundLoader.stopSound("dr_loop.wav");
                } else { //else not playing, then play
                    SoundLoader.playSound("dr_loop.wav");
                }
                //toggle the boolean switch
                cc.setThemeMusic(!cc.isThemeMusic());
                break;
            default:
                break;

        }

    }

    @Override
    // does nothing, but we need it b/c of KeyListener contract
    public void keyTyped(KeyEvent e) {
    }

}


