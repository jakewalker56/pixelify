Pixelfy is a programatic image editing utility that turns images into stylazed pixelated versions of themselves.  It roughly follows three steps:
1. Cluster the pixel colors present in the image into a small palette
2. Merge pixels into squares and color them the palette color nearest to the average of the pixels in that square
3. Apply various style artifacts to the squares

I built this tool over a weekend after thumbing through the [Map Design Toolbox](https://us.gestalten.com/products/map-design-toolbox) and wishing I could generate maps similar to those.

# Usage
    usage: pixelfy.py [-h] [-width WIDTH] [-height HEIGHT] [-shift SHIFT] [-clusters CLUSTERS] [-borderpix BORDERPIX]
                  [-rounding ROUNDING] [-roundradius ROUNDRADIUS] [-shading SHADING] [-text TEXT] -image IMAGE

    Pixelfy and stylize images

    optional arguments:
      -h, --help            show this help message and exit
      -width WIDTH          an integer for the width of the pixelized squares (default: 20)
      -height HEIGHT        an integer for the height of the pixelized squares (default: 20)
      -shift SHIFT          a float for the shift angle of the pixelized squares (1.0 = shift by 1 pixel per row)
                        (default: 0.0)
      -clusters CLUSTERS    an integer for the number of kmeans clusters to fit to the color palette of the image
                        (default: 7)
      -borderpix BORDERPIX  an integer for the number of pixels to blend between squares (default: 2)
      -rounding ROUNDING    whether or not to round corners (default: True)
      -roundradius ROUNDRADIUS
                        a float to adjust the radius when rounding cordners. Higher numbers make the corner less
                        rounded. Negative numbers reduce the corner radius, which tends to look bad and is not
                        recommended (default: 0)
      -shading SHADING      whether or not to apply blended shading to edges with different colors (default: False)
      -text TEXT            whether or not to add OCR text onto resulting image (requires Google Cloud Vision credentials)
                        (default: False)
      -image IMAGE          image to pixelfy


# Constraints
Some options don't go well together.  Some examples include: 
- if you use a non-zero shift, it is recomended that you leave shading set to false.  Shading with shift causes blending along edges that no longer map to neighboring pixel coordinates, giving some weird results.
- If you use a non-zero shift, it is recommended tat you set rounding to false.  The angled boxes make it appear as if corners exist, but they're not actual corners in the "both neighboring pixels are different colors" sense, so they don't get rounded.
- If you set shading to true, it is recommended that you set rounding to false.  The problem with setting both to true is the edge opposite the rounded corner will also shade, leaving obvious lines around rounded corners.  You can get away with using rounding and shading if you have a high roundradius value, but otherwise it will probably look bad.  This is fixable in principle, just a lot of work that didn't seem worth it to do.
- Sometimes corners that look like they should be rounded aren't.  This typically happens because the two neighboring colors are different, and it's therefore unclear what color to fill in behind the rounded corners
- Text doesn't rotate correctly when inserted back into the image.  This is because PIL doesn't allow it.  There's a workaround to print text to a blank image, rotate the image, then paste it into your original, but I haven't gotten to it yet

# Examples
pixelfy.py -image example1.png -output output1.png -clusters 6 -width 30 -height 30 -roundradius 2
![example 1](https://github.com/jakewalker56/pixelify/blob/master/images/example1.png) 
![output 1](https://github.com/jakewalker56/pixelify/blob/master/images/output1.png)


pixelfy.py -image example2.png -output output2.png -clusters 8 -width 20 -height 30 -shift 0.2 -roundradius 1
![example 2](https://github.com/jakewalker56/pixelify/blob/master/images/example2.png) 
![output 2](https://github.com/jakewalker56/pixelify/blob/master/images/output2.png)

pixelfy.py -image example3.png -output output3.png -clusters 8 -width 8 -height 8 -shading true -rounding false -text true -textcolor white
![example 3](https://github.com/jakewalker56/pixelify/blob/master/images/example3.png) 
![output 3](https://github.com/jakewalker56/pixelify/blob/master/images/output3.png)

pixelfy.py -image example4.png -output output4.png -clusters 2 -width 20 -height 10
![example 4](https://github.com/jakewalker56/pixelify/blob/master/images/example4.png) 
![output 4](https://github.com/jakewalker56/pixelify/blob/master/images/output4.png)

pixelfy.py -image example5.png -output output5.png -clusters 2 -width 50 -height 50
![example 5](https://github.com/jakewalker56/pixelify/blob/master/images/example5.png) 
![output 5](https://github.com/jakewalker56/pixelify/blob/master/images/output5.png)

pixelfy.py -image example6.png -output output6.png -clusters 4 -width 50 -height 50 -shading true -borderpix 10
![example 6](https://github.com/jakewalker56/pixelify/blob/master/images/example6.png) 
![output 6](https://github.com/jakewalker56/pixelify/blob/master/images/output6.png)

pixelfy.py -image example7.png -output output7.png -clusters 2 -width 10 -height 10 -roundradius 1
![example 7](https://github.com/jakewalker56/pixelify/blob/master/images/example7.png) 
![output 7](https://github.com/jakewalker56/pixelify/blob/master/images/output7.png)

pixelfy.py -image example8.png -output output8.png -clusters 3 -width 3 -height 3

pixelfy.py -image example8.png -output output9.png -clusters 4 -width 3 -height 3

pixelfy.py -image example8.png -output output10.png -clusters 10 -width 3 -height 3

![example 8](https://github.com/jakewalker56/pixelify/blob/master/images/example8.png) 
![output 8](https://github.com/jakewalker56/pixelify/blob/master/images/output8.png)
![output 9](https://github.com/jakewalker56/pixelify/blob/master/images/output9.png)
![output 10](https://github.com/jakewalker56/pixelify/blob/master/images/output10.png)
