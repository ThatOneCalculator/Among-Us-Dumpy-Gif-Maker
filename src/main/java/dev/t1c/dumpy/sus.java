package dev.t1c.dumpy;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.awt.image.BufferedImageOp;
import java.awt.image.LookupOp;
import java.awt.image.LookupTable;
import java.awt.image.RenderedImage;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;

import javax.imageio.IIOImage;
import javax.imageio.ImageIO;
import javax.imageio.ImageTypeSpecifier;
import javax.imageio.ImageWriteParam;
import javax.imageio.ImageWriter;
import javax.imageio.metadata.IIOInvalidTreeException;
import javax.imageio.metadata.IIOMetadata;
import javax.imageio.metadata.IIOMetadataNode;
import javax.imageio.stream.ImageOutputStream;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.UIManager;
import javax.swing.filechooser.FileFilter;
import javax.swing.filechooser.FileSystemView;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

public class sus {

	// Put in the directory where you extracted this
	public static String dir = "[DIRECTORY]";

	public static Color c = Color.decode("#C51111");
	public static Color c2 = new Color(122, 8, 56);
	public static double shadeDefault = 0.00;

	// MAIN
	public static void main(String[] args) throws Exception {

		var main = new sus();
		String dotSlash = "./";
		String background = "dumpy/black.png";
		boolean windows = isWindows();
		if (windows) {
			dotSlash = ".\\";
		}

		String input = "";
		String extraoutput = "";
		String mode = "default";

		int ty = 10; // width value

		Options options = new Options();

		Option li = Option.builder().longOpt("lines").hasArg().desc("Changes the number of lines (defaults to 10)")
				.build();
		Option fl = Option.builder().longOpt("file").hasArg().desc("Path to file, hides file picker").build();
		Option bk = Option.builder().longOpt("background").hasArg().desc("Path to custom background").build();
		Option md = Option.builder().longOpt("mode").hasArg()
				.desc("Crewmate mode, currently supports default, furry, sans, spamton, isaac, and bounce").build();
		Option eo = Option.builder().longOpt("extraoutput").hasArg().desc("Appends text to output files").build();
		Option hp = Option.builder().longOpt("help").desc("Shows this message").build();
		options.addOption(li);
		options.addOption(fl);
		options.addOption(bk);
		options.addOption(md);
		options.addOption(eo);
		options.addOption(hp);

		HelpFormatter formatter = new HelpFormatter();

		CommandLineParser parser = new DefaultParser();
		CommandLine cmd = parser.parse(options, args);

		if (cmd.hasOption("help")) {
			formatter.printHelp("Among Us Dumpy Gif Maker\nAll flags are optional.", options);
			System.exit(0);
		}

		if (cmd.hasOption("lines")) {
			try {
				ty = Integer.parseInt(cmd.getOptionValue("lines"));
			} catch (NumberFormatException e) {
				System.err.println("Lines value is not a number!");
				System.exit(1);
			}
		}

		if (cmd.hasOption("background")) {
			background = cmd.getOptionValue("background");
		}

		if (cmd.hasOption("file")) {
			input = cmd.getOptionValue("file");
		} else {
			input = pickFile();
		}

		if (cmd.hasOption("mode")) {
			mode = cmd.getOptionValue("mode");
			String[] validModes = { "default", "furry", "sans", "spamton", "isaac", "bounce" };
			if (!Arrays.asList(validModes).contains(mode)) {
				System.out.println("Mode has to be default, furry, sans, spamton isaac, or bounce!");
				System.exit(1);
			}
		}

		if (cmd.hasOption("extraoutput")) {
			extraoutput = cmd.getOptionValue("extraoutput");
		}

		BufferedImage bg;

		try {
			InputStream blackImg = main.getResource(background);
			bg = ImageIO.read(blackImg);
		} catch (Exception e) {
			File blackImg = new File(background);
			bg = ImageIO.read(blackImg);
		}

		BufferedImage r = ImageIO.read(new File(input));

		// Calculates size from height
		double txd = (double) r.getWidth() / (double) r.getHeight();
		int tx = (int) Math.round((double) ty * txd * 0.862);

		// Prepares source image
		BufferedImage image = toBufferedImage(r.getScaledInstance(tx, ty, Image.SCALE_SMOOTH));

		// sets up loop vars
		int bufferedImageArraySize = 6;
		int count1Check = 6;
		int count2Reset = 5;
		int sourceX = 74;
		int sourceY = 63;
		String modestring = "";

		if (mode.equals("furry")) {
			bufferedImageArraySize--;
			count1Check--;
			count2Reset--;
			modestring = "_twist";
		}

		else if (mode.equals("isaac")) {
			modestring = "_isaac";
		}

		else if (mode.equals("sans")) {
			modestring = "_sans";
		}

		else if (mode.equals("spamton")) {
			modestring = "_spamton";
			sourceY = 66;
		}

		else if (mode.equals("bounce")) {
			bufferedImageArraySize -= 2;
			count1Check -= 2;
			count2Reset -= 2;
			sourceY = 74;
			modestring = "_bounce";
		}

		// Sets up BG
		int pad = 10;
		int ix = (tx * sourceX) + (pad * 2);
		int iy = (ty * sourceY) + (pad * 2);

		// Actually makes the frames
		BufferedImage[] frames = new BufferedImage[bufferedImageArraySize];

		// these constants are now variables.
		double fac = 1.00;
		int mox = 74;
		int moy = 63;
		BufferedImage[] moguses = new BufferedImage[bufferedImageArraySize];
		for (int it = 0; it < bufferedImageArraySize; it++) {
			var temp = main.getResource("dumpy/" + it + modestring + ".png");
			moguses[it] = ImageIO.read(temp);
		}

		// dynamic resizer
		if (ix > 1000 || iy > 1000) {
			if (ix > iy) {
				fac = 1000.0 / (double) ix;
			} else {
				fac = 1000.0 / (double) iy;
			}
			// Resizes crewmates
			mox = (int) Math.round((double) mox * fac);
			moy = (int) Math.round((double) moy * fac);
			for (int itt = 0; itt < bufferedImageArraySize; itt++) {
				moguses[itt] = toBufferedImage(moguses[itt].getScaledInstance(mox, moy, Image.SCALE_DEFAULT));
			}
			// Resizing for BG
			pad = (int) ((double) pad * fac);
			ix = (mox * tx) + (pad * 2);
			iy = (moy * ty) + (pad * 2);
		}

		// Plots crewmates
		CountDownLatch l = new CountDownLatch(frames.length);
		for (int index = 0; index < frames.length; index++) {
			final int indexx = index;
			// "Finalized series" of variables. To fix "final or effectively final" errors.
			final BufferedImage F_bg = bg;
			final int F_ty = ty;
			final int F_tx = tx;
			final int F_count1Check = count1Check;
			final int F_count2Reset = count2Reset;
			final String F_dotSlash = dotSlash;
			final String F_extraoutput = extraoutput;
			final int ixF = ix; // new series of "modified" variables
			final int iyF = iy;
			final int moxF = mox;
			final int moyF = moy;
			final int padF = pad;
			// Start of new thread
			new Thread(() -> {
				try {
					// bg
					frames[indexx] = toBufferedImage(F_bg.getScaledInstance(ixF, iyF, Image.SCALE_SMOOTH));

					// counts. One for iterating across frames and the other for the line reset
					int count = indexx;
					int count2 = indexx;

					// iterates through pixels
					for (int y = 0; y < F_ty; y++) {
						for (int x = 0; x < F_tx; x++) {

							// Grabs appropriate pixel frame
							BufferedImage pixel = moguses[count]; // No more constant reading!
							pixel = shader(pixel, image.getRGB(x, y));
							// overlays it (if not null)
							if (pixel != null) {
								frames[indexx] = overlayImages(frames[indexx], pixel, (x * moxF) + padF,
										(y * moyF) + padF);
							}

							// Handles animating
							count++;
							if (count == F_count1Check) {
								count = 0;
							}
						}
						// Handles line resets
						count2--;
						if (count2 == -1) {
							count2 = F_count2Reset;
						}
						count = count2;
					}
					// Writes finished frames
					ImageIO.write(frames[indexx], "PNG", new File(F_dotSlash + "F_" + indexx + F_extraoutput + ".png"));

					// Gives an idea of progress
					System.out.println(indexx);
					l.countDown();
				} catch (Exception e) {
					e.printStackTrace();
				}
			}).start();
		}
		l.await();
		// Sets output file name
		String output = dotSlash + "dumpy" + extraoutput + ".gif";

		// Combines frames into final GIF
		System.out.println("Converting....");
		runCmd("convert -delay 1x20 -loop 0 -alpha set -dispose 2 " + dotSlash + "F_*" + extraoutput + ".png  "
				+ output);
		boolean win = isWindows();

		String[] filenames = new String[] { dotSlash + "F_0" + extraoutput + ".png",
				dotSlash + "F_1" + extraoutput + ".png", dotSlash + "F_2" + extraoutput + ".png",
				dotSlash + "F_3" + extraoutput + ".png", dotSlash + "F_4" + extraoutput + ".png",
				dotSlash + "F_5" + extraoutput + ".png" };

		for (String i : filenames) {
			try {
				if (win) {
					runCmd("del " + i);
				} else {
					runCmd("rm " + i);
				}
			} catch (Exception e) {
			}
		}
		System.out.println("Done.");
	}

	public static BufferedImage resizeImage(BufferedImage originalImage, int targetWidth, int targetHeight)
			throws IOException {
		Image resultingImage = originalImage.getScaledInstance(targetWidth, targetHeight, Image.SCALE_DEFAULT);
		BufferedImage outputImage = new BufferedImage(targetWidth, targetHeight, BufferedImage.TYPE_INT_ARGB);
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
		BufferedImage bimage = new BufferedImage(img.getWidth(null), img.getHeight(null), BufferedImage.TYPE_INT_ARGB);

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

	// New pixel shader
	public static BufferedImage shader(BufferedImage t, int pRgb) {
		Color entry = new Color(pRgb);
		// alpha check
		int WHY = (pRgb >> 24) & 0xFF;
		long lim = Math.round(255.0 * 0.07);
		if (WHY < lim) {
			return null;
		}
		// brightness check. If the pixel is too dim, the brightness is floored to the
		// standard "black" level.
		float[] hsb = new float[3];
		Color.RGBtoHSB(entry.getRed(), entry.getGreen(), entry.getBlue(), hsb);
		float blackLevel = 0.200f;
		if (hsb[2] < blackLevel) {
			entry = new Color(Color.HSBtoRGB(hsb[0], hsb[1], blackLevel));
		}
		// "Blue's Clues" shadow fix: Fixes navy blue shadows.
		shadeDefault = 0.66;
		double factor = Math.abs(shadeDefault - (double) hsb[0]);
		factor = (1.0 / 6.0) - factor;
		if (factor > 0) {
			factor = factor * 2;
			// System.out.println(shadeDefault + ", " + factor);
			shadeDefault = shadeDefault - factor;
		}
		// shading.
		Color shade = null;
		try {
			shade = new Color((int) ((double) entry.getRed() * shadeDefault),
					(int) ((double) entry.getGreen() * shadeDefault), (int) ((double) entry.getBlue() * shadeDefault));
		} catch (IllegalArgumentException iae) {
			System.out.println("ERROR: " + shadeDefault + ", " + factor);
		}
		Color.RGBtoHSB(shade.getRed(), shade.getGreen(), shade.getBlue(), hsb);
		hsb[0] = hsb[0] - 0.0635f;
		if (hsb[0] < 0.0f) {
			hsb[0] = 1.0f + hsb[0];
		}
		shade = new Color(Color.HSBtoRGB(hsb[0], hsb[1], hsb[2]));
		// fills in img
		BufferedImageOp lookup = new LookupOp(new ColorMapper(c, entry), null);
		BufferedImageOp lookup2 = new LookupOp(new ColorMapper(c2, shade), null);
		t = toARGB(t);
		BufferedImage convertedImage = lookup.filter(t, null);
		convertedImage = lookup2.filter(convertedImage, null);
		return convertedImage;
	}

	// Indexed image error (https://stackoverflow.com/a/19594979)
	public static BufferedImage toARGB(Image i) {
		BufferedImage rgb = new BufferedImage(i.getWidth(null), i.getHeight(null), BufferedImage.TYPE_INT_ARGB);
		rgb.createGraphics().drawImage(i, 0, 0, null);
		return rgb;
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

/*
 * Shamelessly stolen from
 * https://memorynotfound.com/generate-gif-image-java-delay-infinite-loop-
 * example/
 */

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

// Color replacement solution from https://stackoverflow.com/a/27464772
class ColorMapper extends LookupTable {

	private final int[] from;
	private final int[] to;

	public ColorMapper(Color from, Color to) {
		super(0, 4);

		this.from = new int[] { from.getRed(), from.getGreen(), from.getBlue(), from.getAlpha(), };
		this.to = new int[] { to.getRed(), to.getGreen(), to.getBlue(), to.getAlpha(), };
	}

	@Override
	public int[] lookupPixel(int[] src, int[] dest) {
		if (dest == null) {
			dest = new int[src.length];
		}

		int[] newColor = (Arrays.equals(src, from) ? to : src);
		System.arraycopy(newColor, 0, dest, 0, newColor.length);

		return dest;
	}

}
