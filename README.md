# npsize
nanoparticle size & interparticle space measurement

This program is for NP size measurement & interparticle space from Hitachi HT 7700 TEM images. 

To use the program, download the 'mag' folder and 'npsize_multi.py'/'npips_multi.py'. Put images in a folder starting with "sphere/cube/rod" and run the codes. The program will open all the jpg/tif files, then label and measures the sizes & interparticle spaces of the particles. The particles measured will be highlighted with green rectangles/circles and index number. The interparticle space will be labelled with blue lines. Press 'n' on keyboard to open the next image. Press 'Esc' to quit. After finishing, all the labelled NP images and the corresponding measurements will be saved in newly generated files.

Manual adjustments:
1. Use the trackbar on top to change the size of the binding shapes for more precise measurements.
2. Enlarge part of the image by dragging on the original image.
3. Change the parameters on top of the codes.
