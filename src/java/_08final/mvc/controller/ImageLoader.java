package _08final.mvc.controller;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.HashMap;
import java.util.Map;

/*
Place all .png image assets in src/resources/imgs (or its subdirectories). Maven copies src/resources
onto the classpath (see pom.xml), so images are resolved via the classpath rather than the current
working directory. All raster images are loaded in static context prior to runtime.
 */
public class ImageLoader {

    //classpath root under which the images live, e.g. keys look like "/imgs/fal/falcon125.png"
    private static final String IMAGES_ROOT = "/imgs";

    private static final Map<String, BufferedImage> IMAGE_MAP = loadImageMap();

    private static Map<String, BufferedImage> loadImageMap() {
        try {
            URL imgsUrl = ImageLoader.class.getResource(IMAGES_ROOT);
            Path root;
            Path keyBase;
            if (imgsUrl != null) {
                //resources are on the classpath (e.g. target/classes/imgs)
                root = Paths.get(imgsUrl.toURI());
                keyBase = root.getParent();
            } else {
                //fall back to the shared source tree if resources were not copied to the classpath
                root = Paths.get("src/resources/imgs");
                keyBase = Paths.get("src/resources");
            }
            return loadPngImages(root, keyBase);
        } catch (IOException | URISyntaxException e) {
            e.printStackTrace();
            //degrade gracefully rather than failing class initialization
            return new HashMap<>();
        }
    }

    /*
     Walks the directory hierarchy at rootDirectory and returns a Map<String, BufferedImage> keyed by
     classpath-style paths relative to keyBase, e.g. "/imgs/fal/falcon125.png".
     */
    private static Map<String, BufferedImage> loadPngImages(Path rootDirectory, Path keyBase) throws IOException {
        Map<String, BufferedImage> pngImages = new HashMap<>();
        Files.walkFileTree(rootDirectory, new SimpleFileVisitor<Path>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                String name = file.toString().toLowerCase();
                if (name.endsWith(".png") && !name.contains("do_not_load.png")) {
                    try {
                        BufferedImage bufferedImage = ImageIO.read(file.toFile());
                        if (bufferedImage != null) {
                            //build a stable, classpath-style key, e.g. "/imgs/fal/falcon125.png"
                            String key = ("/" + keyBase.relativize(file)).replace("\\", "/").toLowerCase();
                            pngImages.put(key, bufferedImage);
                        }
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
                return FileVisitResult.CONTINUE;
            }
            @Override
            public FileVisitResult visitFileFailed(Path file, IOException exc) {
                // Handle the error here if necessary
                return FileVisitResult.CONTINUE;
            }
        });
        return pngImages;
    }


    //fetch the image from the existing static map
    public static BufferedImage getImage(String imagePath) {
            return IMAGE_MAP.get(imagePath.toLowerCase());

    }


}
