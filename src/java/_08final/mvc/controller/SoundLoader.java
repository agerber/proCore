package _08final.mvc.controller;


import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Clip;
import javax.sound.sampled.LineEvent;
import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.UnsupportedAudioFileException;

public class SoundLoader {

	//classpath root under which the sounds live, e.g. "/sounds/dr_loop.wav". Maven copies
	//src/resources onto the classpath (see pom.xml), so sounds are resolved via the classpath
	//rather than the current working directory.
	private static final String SOUNDS_ROOT = "/sounds";

	/* A Looped clip is one that plays for an indefinite time until you call the stopSound() method. Non-looped
		clips, which may have multiple instances that play concurrently, are queued onto the ThreadPoolExecutor
		below. Make sure to place all sounds directly in the src/resources/sounds directory and suffix any looped
		clips with _loop.
	 */
	private static final Map<String, Clip> LOOPED_CLIPS_MAP = loadLoopedSounds();

	/* ThreadPoolExecutor for playing non-looped sounds. Limit the number of threads to 5 at a time. Sounds that can
	be played simultaneously must be queued onto the soundExecutor at runtime.
	 */
	private static final ThreadPoolExecutor soundExecutor = (ThreadPoolExecutor) Executors.newFixedThreadPool(5);

	//cache the raw bytes of non-looped clips so repeated plays don't re-read the classpath each time
	private static final Map<String, byte[]> ONE_SHOT_BYTES = new ConcurrentHashMap<>();

	private static boolean loopedCondition(String str){
		return str.toLowerCase().endsWith("_loop.wav");
	}

	// Load all looping sounds in the static context. Degrades gracefully (empty map) if the
	// /sounds resource cannot be located, rather than failing class initialization.
	private static Map<String, Clip> loadLoopedSounds() {
		Map<String, Clip> soundClips = new HashMap<>();
		try {
			URL soundsUrl = SoundLoader.class.getResource(SOUNDS_ROOT);
			Path rootDirectory = (soundsUrl != null)
					? Paths.get(soundsUrl.toURI())
					: Paths.get("src/resources/sounds");
			Files.walkFileTree(rootDirectory, new SimpleFileVisitor<Path>() {
				@Override
				public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
					if (loopedCondition(file.toString())) {
						try {
							String fileName = file.getFileName().toString();
							Clip clip = getLoopClip(fileName);
							if (clip != null) {
								soundClips.put(fileName, clip);
							}
						} catch (Exception e) {
							e.printStackTrace();
						}
					}
					return FileVisitResult.CONTINUE;
				}

				@Override
				public FileVisitResult visitFileFailed(Path file, IOException exc) {
					return FileVisitResult.CONTINUE;
				}
			});
		} catch (IOException | URISyntaxException e) {
			e.printStackTrace();
		}
		return soundClips;
	}

	private static Clip getLoopClip(String fileName) throws Exception {
		String relativePath = SOUNDS_ROOT + "/" + fileName;
		try (InputStream audioSrc = SoundLoader.class.getResourceAsStream(relativePath)) {
			if (audioSrc == null) {
				throw new IOException("No such sound file exists at " + relativePath);
			}
			InputStream bufferedIn = new BufferedInputStream(audioSrc);
			AudioInputStream aisStream = AudioSystem.getAudioInputStream(bufferedIn);
			Clip clip = AudioSystem.getClip();
			clip.open(aisStream);
			return clip;
		} catch (UnsupportedAudioFileException | IOException | LineUnavailableException e) {
			e.printStackTrace();
			throw e;
		}
	}


	// Used for both looped and non-looped clips
	public static void playSound(final String strPath) {
		//Looped clips are fetched from the existing static LOOPED_CLIPS_MAP at runtime.
		if (loopedCondition(strPath)){
			Clip clip = LOOPED_CLIPS_MAP.get(strPath);
			if (clip != null) {
				clip.loop(Clip.LOOP_CONTINUOUSLY);
			}
			return;
		}
		//Non-looped clips are enqueued onto the executor-threadpool at runtime.
		soundExecutor.execute(() -> {
			try {
				byte[] audioBytes = getOneShotBytes(strPath);
				if (audioBytes == null) {
					System.err.println("No such sound file on classpath: " + SOUNDS_ROOT + "/" + strPath);
					return;
				}
				Clip clip = AudioSystem.getClip();
				//close the clip once playback completes so native audio lines are not leaked
				clip.addLineListener(event -> {
					if (event.getType() == LineEvent.Type.STOP) {
						event.getLine().close();
					}
				});
				AudioInputStream aisStream = AudioSystem.getAudioInputStream(
						new BufferedInputStream(new ByteArrayInputStream(audioBytes)));
				clip.open(aisStream);
				clip.start();
			} catch (Exception e) {
				System.err.println(e.getMessage());
			}
		});

	}

	//load-and-cache the raw bytes of a one-shot sound so we avoid re-reading the classpath on every play
	private static byte[] getOneShotBytes(String strPath) throws IOException {
		byte[] cached = ONE_SHOT_BYTES.get(strPath);
		if (cached != null) return cached;
		try (InputStream in = SoundLoader.class.getResourceAsStream(SOUNDS_ROOT + "/" + strPath)) {
			if (in == null) return null;
			byte[] bytes = in.readAllBytes();
			ONE_SHOT_BYTES.put(strPath, bytes);
			return bytes;
		}
	}

	//Non-looped clips can not be stopped, they simply expire on their own. Calling this method on a
	// non-looped clip will do nothing.
	public static void stopSound(final String strPath) {
		if (!loopedCondition(strPath)) return;
		Clip clip = LOOPED_CLIPS_MAP.get(strPath);
		if (clip != null) {
			clip.stop();
		}
	}


}
