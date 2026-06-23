package _08final.mvc.controller;

import javax.imageio.ImageIO;
import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.HashMap;
import java.awt.image.BufferedImage;
import java.nio.file.Paths;
import java.util.Map;
import java.util.Objects;

/*
Place all .png image assets in this directory src/resources/imgs or its subdirectories.
All raster images loaded in static context prior to runtime.
 */
public class ImageLoader {

    // Resources are shared with the Python project and read from the filesystem (relative to the
    // project root / user.dir). Keys are stored relative to this base, e.g. "/imgs/fal/falcon125.png".
    private static final String RESOURCES_BASE = "src/resources";

    private static Map<String, BufferedImage> IMAGE_MAP = null;
    static {
            Path rootDirectory = Paths.get(RESOURCES_BASE + "/imgs");
            Map<String, BufferedImage> localMap = null;
            try {
                localMap = loadPngImages(rootDirectory);
            } catch (IOException e) {
                e.fillInStackTrace();
            }
            IMAGE_MAP = localMap;
    }

    /*
     Walks the directory and sub-directories at root src/resources/imgs and returns a Map<String, BufferedImage>
     of images in that file hierarcy.
     */
    private static Map<String, BufferedImage> loadPngImages(Path rootDirectory) throws IOException {
        Map<String, BufferedImage> pngImages = new HashMap<>();
        Files.walkFileTree(rootDirectory, new SimpleFileVisitor<Path>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                if (file.toString().toLowerCase().endsWith(".png")
                        && !file.toString().toLowerCase().contains("do_not_load.png")) {
                    try {
                        BufferedImage bufferedImage = ImageIO.read(file.toFile());
                        if (bufferedImage != null) {
                            //strip RESOURCES_BASE ("src/resources") so keys are simple, e.g. "/imgs/fal/falcon125.png"
                            pngImages.put(file.toString().toLowerCase().replace("\\", "/").substring(RESOURCES_BASE.length()), bufferedImage);
                        }
                    } catch (IOException e) {
                        e.fillInStackTrace();
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


    //fetch the image from existing static map
    public static BufferedImage getImage(String imagePath) {
            return IMAGE_MAP.get(imagePath.toLowerCase());

    }


}
