package dev.t1c.dumpy;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.awt.image.RenderedImage;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;

import javax.imageio.IIOImage;
import javax.imageio.ImageIO;
import javax.imageio.ImageTypeSpecifier;
import javax.imageio.ImageWriteParam;
import javax.imageio.ImageWriter;
import javax.imageio.metadata.IIOInvalidTreeException;
import javax.imageio.metadata.IIOMetadata;
import javax.imageio.metadata.IIOMetadataNode;
import javax.imageio.stream.FileImageOutputStream;
import javax.imageio.stream.ImageOutputStream;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.UIManager;
import javax.swing.filechooser.FileFilter;
import javax.swing.filechooser.FileSystemView;

public class sus {

	// Put in the directory where you extracted this
	public static String dir = "[DIRECTORY]";

	// Hex color array
	public static String[] HEXES;

	// MAIN
	public static void main(String[] args) throws Exception {

		var main = new sus();
		String dotSlash = "./";
		boolean dither = false;
		boolean windows = isWindows();
		if (windows) {
			dotSlash = ".\\";
		}

		String input = "";
		String extraoutput = "";
		boolean needFile = true;

		int ty = 9; // width value

		if (args.length > 0) {
			if (args[0] != null) {
				if (args[0].toLowerCase().indexOf("help") != -1) {
					System.out.println(
							"""

									`java -jar Among-Us-Dumpy-Gif-Maker-1.6.1-all.jar lines true/false filepath` for adding arguments

									*All arguments optional!*
									- `lines` is the number of lines, which defaults to 9.
									- `true/false` is whether to dither, which generally looks better at higher resolutions but not at lower ones.
									- `filepath` is a filepath to give it instead of using the file picker.""");
					System.exit(0);
				}
				if (args[0].toLowerCase().indexOf("version") != -1) {
					System.out.println("Version 1.6.1");
					System.exit(0);
				}
				try {
					ty = Integer.parseInt(args[0]);
				} catch (NumberFormatException e) {
					System.err.println("Not a number!");
				}
			}
			if (args.length >= 2 && args[1] != null) {
				if (args[1].toLowerCase().indexOf("true") != -1) {
					dither = true;
				}
			}
			if (args.length >= 3 && args[2] != null) {
				input = args[2];
				needFile = false;
			}

			if (args.length >= 4 && args[3] != null) {
				extraoutput = args[3];
				needFile = false;
			}
		}

		if (needFile) {
			input = pickFile();
		}

		InputStream imgInput = main.getResource("dumpy/colors.png");
		BufferedImage c = ImageIO.read(imgInput);
		HEXES = new String[24];
		for (int i = 0; i < HEXES.length; i++) {
			try {
				HEXES[i] = Integer.toHexString(c.getRGB(i, 0)).substring(2).toUpperCase();
			} catch (Exception e) {
				System.out.println(i);
			}
		}

		// Gets BG and input file
		InputStream blackImg = main.getResource("dumpy/black.png");
		BufferedImage bg = ImageIO.read(blackImg);
		BufferedImage r = ImageIO.read(new File(input));

		// Calculates size from height
		double txd = (double) r.getWidth() / (double) r.getHeight();
		int tx = (int) Math.round((double) ty * txd * 0.862);

		// Prepares source image
		BufferedImage image = Dither
				.floydSteinbergDithering(toBufferedImage(r.getScaledInstance(tx, ty, Image.SCALE_SMOOTH)), dither);

		// Actually makes the frames
		BufferedImage[] frames = new BufferedImage[6];

		// Sets up BG
		int pad = 10;
		int ix = (tx * 74) + (pad * 2);
		int iy = (ty * 63) + (pad * 2);

		// Plots crewmates
		for (int index = 0; index < frames.length; index++) {
			// bg
			frames[index] = toBufferedImage(bg.getScaledInstance(ix, iy, Image.SCALE_SMOOTH));

			// counts. One for iterating across frames and the other for the line reset
			int count = index;
			int count2 = index;

			// iterates through pixels
			for (int y = 0; y < ty; y++) {
				for (int x = 0; x < tx; x++) {

					// Grabs appropriate pixel frame
					var pixelI = main.getResource("dumpy/" + count + "-"
							+ Integer.toHexString(image.getRGB(x, y)).substring(2).toUpperCase() + ".png");
					BufferedImage pixel = ImageIO.read(pixelI);
					// overlays it
					frames[index] = overlayImages(frames[index], pixel, (x * 74) + pad, (y * 63) + pad);

					// Handles animating
					count++;
					if (count == 6) {
						count = 0;
					}
				}
				// Handles line resets
				count2--;
				if (count2 == -1) {
					count2 = 5;
				}
				count = count2;
			}
			// Writes finished frames
			ImageIO.write(frames[index], "PNG", new File(dotSlash + "F_" + index + extraoutput + ".png"));

			// Gives an idea of progress
			System.out.println(index);
		}
		// Sets output file name
		String output = dotSlash + "dumpy" + extraoutput + ".gif";

		// Combines frames into final GIF
		System.out.println("Converting....");
		BufferedImage first = ImageIO.read(new File(dotSlash + "F_1" + extraoutput + ".png"));
		ImageOutputStream imageoutput = new FileImageOutputStream(new File(output));

		GifSequenceWriter writer = new GifSequenceWriter(imageoutput, first.getType(), 50, true);
		writer.writeToSequence(first);

		File[] images = new File[] {
			new File(dotSlash + "F_2" + extraoutput + ".png"),
			new File(dotSlash + "F_3" + extraoutput + ".png"),
			new File(dotSlash + "F_4" + extraoutput + ".png"),
			new File(dotSlash + "F_5" + extraoutput + ".png"),
		};

		for (File i : images) {
			try {
				BufferedImage next = ImageIO.read(i);
				writer.writeToSequence(next);
			} catch (IOException e) {
				System.out.println("Couldn't add " + i.toString());
			}
		}

		writer.close();
		imageoutput.close();
		boolean win = isWindows();
		if (win) {
			runCmd("del .\\F_*");
		} else {
			runCmd("rm ./F_*");
		}

		// Resizes if need be
		BufferedImage resize = ImageIO.read(new File(output));
		if (resize.getHeight() > 1000 || resize.getWidth() > 1000) {
			// BufferedImage rz = resizeImage(resize, 500, resize.getWidth());
			// ImageIO.write(rz, "gif", new File(output));
			runCmd("convert " + output + " -resize 1000x1000 " + output);
		}
		System.out.println("Done.");
	}

	public static BufferedImage resizeImage(BufferedImage originalImage, int targetWidth, int targetHeight) throws IOException {
		Image resultingImage = originalImage.getScaledInstance(targetWidth, targetHeight, Image.SCALE_DEFAULT);
		BufferedImage outputImage = new BufferedImage(targetWidth, targetHeight, BufferedImage.TYPE_INT_RGB);
		outputImage.getGraphics().drawImage(resultingImage, 0, 0, null);
		return outputImage;
	}

	private InputStream getResource(String filename) {
		var loader = this.getClass().getClassLoader();
		var is = loader.getResourceAsStream(filename);

		if (is == null)
			throw new NullPointerException("got null when retrieving file " + filename);

		return is;
	}

	// Picks file
	public static String pickFile() throws Exception {

		UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
		JFileChooser jfc = new JFileChooser(FileSystemView.getFileSystemView().getHomeDirectory());
		jfc.addChoosableFileFilter(new ImageFilter());
		jfc.setAcceptAllFileFilterUsed(false);

		int returnValue = jfc.showOpenDialog(null);
		// int returnValue = jfc.showSaveDialog(null);

		if (returnValue == JFileChooser.APPROVE_OPTION) {
			File selectedFile = jfc.getSelectedFile();
			String i = selectedFile.getAbsolutePath();
			System.out.println(i);
			return i;
		} else {
			System.exit(0);
			return "";
		}
	}

	// BufferedImage converter from https://stackoverflow.com/a/13605411
	public static BufferedImage toBufferedImage(Image img) {
		if (img instanceof BufferedImage) {
			return (BufferedImage) img;
		}

		// Create a buffered image with transparency
		BufferedImage bimage = new BufferedImage(img.getWidth(null), img.getHeight(null), BufferedImage.TYPE_INT_RGB);

		// Draw the image on to the buffered image
		Graphics2D bGr = bimage.createGraphics();
		bGr.drawImage(img, 0, 0, null);
		bGr.dispose();

		// Return the buffered image
		return bimage;
	}

	// BufferedImage overlayer from
	// http://blog.icodejava.com/482/java-how-to-overlay-one-image-over-another-using-graphics2d-tutorial/
	public static BufferedImage overlayImages(BufferedImage bgImage,

			BufferedImage fgImage, int locateX, int locateY) {

		/**
		 * Doing some preliminary validations. Foreground image height cannot be greater
		 * than background image height. Foreground image width cannot be greater than
		 * background image width.
		 *
		 * returning a null value if such condition exists.
		 */
		if (fgImage.getHeight() > bgImage.getHeight() || fgImage.getWidth() > fgImage.getWidth()) {
			JOptionPane.showMessageDialog(null, "Foreground Image Is Bigger In One or Both Dimensions"
					+ "nCannot proceed with overlay." + "nn Please use smaller Image for foreground");
			return null;
		}

		/** Create a Graphics from the background image **/
		Graphics2D g = bgImage.createGraphics();
		/** Set Antialias Rendering **/
		g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
		/**
		 * Draw background image at location (0,0) You can change the (x,y) value as
		 * required
		 */
		g.drawImage(bgImage, 0, 0, null);

		/**
		 * Draw foreground image at location (0,0) Change (x,y) value as required.
		 */
		g.drawImage(fgImage, locateX, locateY, null);

		g.dispose();
		return bgImage;
	}

	public static boolean isWindows() {
		return System.getProperty("os.name").toLowerCase().startsWith("windows");
	}

	// convenient way to handle Windows commands.
	public static void runCmd(String cmd) throws Exception {
		boolean win = isWindows();
		if (win) {
			// execute windows command
			new ProcessBuilder("cmd", "/c", cmd).inheritIO().start().waitFor();
		} else {
			// execute *nix command
			new ProcessBuilder("sh", "-c", cmd).inheritIO().start().waitFor();
		}
	}
}

// This is an example of Floyd-Steinberg dithering lifted from
// https://gist.github.com/naikrovek/643a9799171d20820cb9.
// It can be enabled and disabled in the main class.
class Dither {
	static class C3 {
		int r, g, b;

		public C3(int c) {
			Color color = new Color(c);
			r = color.getRed();
			g = color.getGreen();
			b = color.getBlue();
		}

		public C3(int r, int g, int b) {
			this.r = r;
			this.g = g;
			this.b = b;
		}

		public C3 add(C3 o) {
			return new C3(r + o.r, g + o.g, b + o.b);
		}

		public int clamp(int c) {
			return Math.max(0, Math.min(255, c));
		}

		public int diff(C3 o) {
			int Rdiff = o.r - r;
			int Gdiff = o.g - g;
			int Bdiff = o.b - b;
			int distanceSquared = Rdiff * Rdiff + Gdiff * Gdiff + Bdiff * Bdiff;
			return distanceSquared;
		}

		public C3 mul(double d) {
			return new C3((int) (d * r), (int) (d * g), (int) (d * b));
		}

		public C3 sub(C3 o) {
			return new C3(r - o.r, g - o.g, b - o.b);
		}

		public Color toColor() {
			return new Color(clamp(r), clamp(g), clamp(b));
		}

		public int toRGB() {
			return toColor().getRGB();
		}
	}

	private static C3 findClosestPaletteColor(C3 c, C3[] palette) {
		C3 closest = palette[0];

		for (C3 n : palette) {
			if (n.diff(c) < closest.diff(c)) {
				closest = n;
			}
		}

		return closest;
	}

	public static BufferedImage floydSteinbergDithering(BufferedImage img, boolean dither) {

		C3[] palette = null;
		palette = new C3[sus.HEXES.length];
		for (int i = 0; i < palette.length; i++) {
			Color c = hex2Rgb(sus.HEXES[i]);
			palette[i] = new C3(c.getRed(), c.getGreen(), c.getBlue());
		}

		int w = img.getWidth();
		int h = img.getHeight();

		C3[][] d = new C3[h][w];

		for (int y = 0; y < h; y++) {
			for (int x = 0; x < w; x++) {
				d[y][x] = new C3(img.getRGB(x, y));
			}
		}

		for (int y = 0; y < img.getHeight(); y++) {
			for (int x = 0; x < img.getWidth(); x++) {

				C3 oldColor = d[y][x];
				C3 newColor = findClosestPaletteColor(oldColor, palette);
				img.setRGB(x, y, newColor.toColor().getRGB());
				if (dither) {
					C3 err = oldColor.sub(newColor);

					if (x + 1 < w) {
						d[y][x + 1] = d[y][x + 1].add(err.mul(7. / 16));
					}

					if (x - 1 >= 0 && y + 1 < h) {
						d[y + 1][x - 1] = d[y + 1][x - 1].add(err.mul(3. / 16));
					}

					if (y + 1 < h) {
						d[y + 1][x] = d[y + 1][x].add(err.mul(5. / 16));
					}

					if (x + 1 < w && y + 1 < h) {
						d[y + 1][x + 1] = d[y + 1][x + 1].add(err.mul(1. / 16));
					}
				}
			}
		}

		return img;
	}

	public static Color hex2Rgb(String colorStr) {
		return new Color(Integer.valueOf(colorStr.substring(0, 2), 16), Integer.valueOf(colorStr.substring(2, 4), 16),
				Integer.valueOf(colorStr.substring(4, 6), 16));
	}
}

class ImageFilter extends FileFilter {
	public final static String JPEG = "jpeg";
	public final static String JPG = "jpg";
	public final static String BMP = "bmp";
	public final static String TIFF = "tiff";
	public final static String TIF = "tif";
	public final static String PNG = "png";

	@Override
	public boolean accept(File f) {
		if (f.isDirectory()) {
			return true;
		}

		String extension = getExtension(f);
		if (extension != null) {
			if (extension.equals(TIFF) || extension.equals(TIF) || extension.equals(BMP) || extension.equals(JPEG)
					|| extension.equals(JPG) || extension.equals(PNG)) {
				return true;
			} else {
				return false;
			}
		}
		return false;
	}

	@Override
	public String getDescription() {
		return "Image file";
	}

	String getExtension(File f) {
		String ext = null;
		String s = f.getName();
		int i = s.lastIndexOf('.');

		if (i > 0 && i < s.length() - 1) {
			ext = s.substring(i + 1).toLowerCase();
		}
		return ext;
	}
}

// Shamelessly stolen from
// https://memorynotfound.com/generate-gif-image-java-delay-infinite-loop-example/

class GifSequenceWriter {

	private ImageWriter writer;
	private ImageWriteParam params;
	private IIOMetadata metadata;

	public GifSequenceWriter(ImageOutputStream out, int imageType, int delay, boolean loop) throws IOException {
		writer = ImageIO.getImageWritersBySuffix("gif").next();
		params = writer.getDefaultWriteParam();

		ImageTypeSpecifier imageTypeSpecifier = ImageTypeSpecifier.createFromBufferedImageType(imageType);
		metadata = writer.getDefaultImageMetadata(imageTypeSpecifier, params);

		configureRootMetadata(delay, loop);

		writer.setOutput(out);
		writer.prepareWriteSequence(null);
	}

	private void configureRootMetadata(int delay, boolean loop) throws IIOInvalidTreeException {
		String metaFormatName = metadata.getNativeMetadataFormatName();
		IIOMetadataNode root = (IIOMetadataNode) metadata.getAsTree(metaFormatName);

		IIOMetadataNode graphicsControlExtensionNode = getNode(root, "GraphicControlExtension");
		graphicsControlExtensionNode.setAttribute("disposalMethod", "none");
		graphicsControlExtensionNode.setAttribute("userInputFlag", "FALSE");
		graphicsControlExtensionNode.setAttribute("transparentColorFlag", "FALSE");
		graphicsControlExtensionNode.setAttribute("delayTime", Integer.toString(delay / 10));
		graphicsControlExtensionNode.setAttribute("transparentColorIndex", "0");

		IIOMetadataNode commentsNode = getNode(root, "CommentExtensions");
		commentsNode.setAttribute("CommentExtension", "Created by: https://memorynotfound.com");

		IIOMetadataNode appExtensionsNode = getNode(root, "ApplicationExtensions");
		IIOMetadataNode child = new IIOMetadataNode("ApplicationExtension");
		child.setAttribute("applicationID", "NETSCAPE");
		child.setAttribute("authenticationCode", "2.0");

		int loopContinuously = loop ? 0 : 1;
		child.setUserObject(
				new byte[] { 0x1, (byte) (loopContinuously & 0xFF), (byte) ((loopContinuously >> 8) & 0xFF) });
		appExtensionsNode.appendChild(child);
		metadata.setFromTree(metaFormatName, root);
	}

	private static IIOMetadataNode getNode(IIOMetadataNode rootNode, String nodeName) {
		int nNodes = rootNode.getLength();
		for (int i = 0; i < nNodes; i++) {
			if (rootNode.item(i).getNodeName().equalsIgnoreCase(nodeName)) {
				return (IIOMetadataNode) rootNode.item(i);
			}
		}
		IIOMetadataNode node = new IIOMetadataNode(nodeName);
		rootNode.appendChild(node);
		return (node);
	}

	public void writeToSequence(RenderedImage img) throws IOException {
		writer.writeToSequence(new IIOImage(img, null, metadata), params);
	}

	public void close() throws IOException {
        writer.endWriteSequence();
    }
}