from PIL import Image
from PIL import ImageFilter
from PIL import ImageDraw
from PIL import ImageFont
from sklearn.cluster import KMeans
import sys
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import pytesseract
from google.cloud import vision
import io
import itertools
import argparse

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(description='Pixelfy and stylize images')
parser.add_argument('-width', default = 20, type = int,
                    help='an integer for the width of the pixelized squares (default: %(default)s)')

parser.add_argument('-height', default = 20, type = int,
                    help='an integer for the height of the pixelized squares (default: %(default)s)')

parser.add_argument('-shift', default = 0.0, type = float,
                    help='a float for the shift angle of the pixelized squares (1.0 = shift by 1 pixel per row) (default: %(default)s)')

parser.add_argument('-clusters', default = 7, type = int,
                    help='an integer for the number of kmeans clusters to fit to the color palette of the image (default: %(default)s)')

parser.add_argument('-borderpix', default = 2, type = int,
                    help='an integer for the number of pixels to blend between squares (default: %(default)s)')

parser.add_argument('-rounding', default = True, type = str2bool,
                    help='whether or not to round corners (default: %(default)s)')

parser.add_argument('-roundradius', default = 0, type = float,
                    help='a float to adjust the radius when rounding cordners. Higher numbers make the corner less rounded.  Negative numbers reduce the corner radius, which tends to look bad and is not recommended (default: %(default)s)')

parser.add_argument('-shading', default = False, type = str2bool,
                    help='whether or not to apply blended shading to edges with different colors (default: %(default)s)')

parser.add_argument('-text', default = False, type = bool,
                    help='whether or not to add OCR text onto resulting image (requires Google Cloud Vision credentials) (default: %(default)s)')

parser.add_argument('-textcolor', required = False, type = str, default = "black",
                    help='string name for the color to print text in')

parser.add_argument('-image', required = True, type = str,
                    help='image to pixelfy')

parser.add_argument('-output', required = True, type = str,
                    help='output path to save pixelfied image')


p = parser.parse_args()
x_stride = p.width
y_stride = p.height
shift = p.shift
border_pix = p.borderpix
round_radius = p.roundradius
do_rounding = p.rounding
do_shading = p.shading
do_ocr = p.text
clusters = p.clusters
filename = p.image
output = p.output
text_color = p.textcolor
#
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def shader(col1, col2):
	return max(col1[0], col1[1], col1[2]) > max(col2[0], col2[1], col2[2])

def color_merge(col1, col2, str1, str2):
	return (int((str1 * col1[0] + str2*col2[0]) / (str1 + str2)), int((str1 * col1[1] + str2*col2[1]) / (str1 + str2)), int((str1 * col1[2] + str2*col2[2]) / (str1 + str2)), 255)

def get_text(path):

    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations[1::] #the first result is just the concatenation of all other results
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return texts

#for filename in ["example1.png"]: #,"image.png", "image2.png", "image3.png", "image4.png"]: #,"image5.png", "image6.png", "image7.png", "image8.png", "image10.png"]:
im = Image.open(filename)

# d = pytesseract.image_to_data(im, output_type=pytesseract.Output.DICT)
# conf_threshold = np.array(list(map(int, d['conf']))) > 60
# text = np.array(d['text'])[conf_threshold]
# left = np.array(d['left'])[conf_threshold]
# top = np.array(d['top'])[conf_threshold]
# boxwidth = np.array(d['width'])[conf_threshold]
# boxheight = np.array(d['height'])[conf_threshold]

palette = []
kmeans = KMeans(n_clusters=clusters, init='k-means++', max_iter=200, n_init=5, random_state=0)
X = Image.Image.getdata(im)
pred_y = kmeans.fit_predict(X)
centers = kmeans.cluster_centers_.tolist()
for x in range(0, len(centers)):
	palette.append((int(centers[x][0]), int(centers[x][1]), int(centers[x][2]), 255))

print(palette)

# for x in range(0,im.width):
# 	for y in range(0,im.height):
# 		rgba = im.getpixel((x,y))
# 		absolute_difference_function = lambda list_tuple : pow(list_tuple[0] - rgba[0],2) + pow(list_tuple[1] - rgba[1],2) + pow(list_tuple[2] - rgba[2],2)
# 		new_rgba = min(palette, key=absolute_difference_function)
# 		im.putpixel((x,y), new_rgba)

arr = [[[0,0,0,255] for y in range(0, int(im.height / y_stride))] for x in range(0,int(im.width / x_stride))]
for x in range(0,int(im.width / x_stride)):#range(int(x_stride / 2),im.width, x_stride):
	for y in range(0, int(im.height / y_stride)):#range(int(y_stride / 2), im.height, y_stride):
		
		#calculate scaled down pixel value by averaging neighboring pixels and mapping to palette
		#TODO: implement voting instead of averaging to deal with complex scenery?
		total = [0, 0, 0]
		for a in range(0,x_stride):
			for b in range(0, y_stride):
				ax = min(max(0, x * x_stride + a), im.width)
				by = min(max(0, y * y_stride + b), im.height)
				pix = im.getpixel((ax, by))
				total[0] = total[0] + pix[0]
				total[1] = total[1] + pix[1]
				total[2] = total[2] + pix[2] 
			#first calculate the average

		arr[x][y][0] = int(total[0] / (x_stride * y_stride))
		arr[x][y][1] = int(total[1] / (x_stride * y_stride))
		arr[x][y][2] = int(total[2] / (x_stride * y_stride))
		absolute_difference_function = lambda list_tuple : pow(list_tuple[0] - arr[x][y][0],2) + pow(list_tuple[1] - arr[x][y][1],2) + pow(list_tuple[2] - arr[x][y][2],2)
		arr[x][y] = min(palette, key=absolute_difference_function)
		

#set background to transparent
for a in range (0,im.width):
	for b in range(0,im.height):
		im.putpixel((a,b), (255,255,255,0))

#render sloped shapes
for x in range(0,int(im.width / x_stride)):
	for y in range(0, int(im.height / y_stride)):
		tl, tr, bl, br = False, False, False, False
		if do_rounding:
			#rounded corners
			if x > 0 and (arr[x-1][y] != arr[x][y]):
				#not on the left side, and the thing directly to the left is a mismatch
				if y > 0 and (arr[x][y-1] == arr[x-1][y]) and (arr[x-1][y-1] != arr[x][y] or shader(arr[x][y], arr[x-1][y])):
					#not on the top, and the thing above matches the thing to the left
					tl = True
				if y < len(arr[0]) - 1 and arr[x][y+1] == arr[x-1][y] and (arr[x-1][y+1] != arr[x][y] or shader(arr[x][y], arr[x-1][y])):
					#not on bottom, and the thing below matches the thing to the left
					bl = True
			if x < len(arr) - 1 and arr[x+1][y] != arr[x][y]:
				#not on the right side, and the thing directly to the right is a mismatch
				if y > 0 and arr[x][y-1] == arr[x+1][y] and (arr[x+1][y-1] != arr[x][y] or shader(arr[x][y], arr[x+1][y])):
					#not on the top, and the thing above matches the thing to the right
					tr = True
				if y < len(arr[0]) - 1 and arr[x][y+1] == arr[x+1][y] and (arr[x+1][y+1] != arr[x][y] or shader(arr[x][y], arr[x+1][y])):
					#not on bottom, and the thing below matches the thing to the right
					br = True
		
		for a in range(0, x_stride):
			for b in range(0, y_stride):
				ax = min(max(0, x * x_stride + a + int((y_stride / 2 - b) * shift)), im.width - 1)
				by = min(max(0, y * y_stride + b), im.height - 1)
				col = arr[x][y]
				
				if do_shading:
					#shade all borders
					if x > 0 and a < border_pix and arr[x-1][y] != arr[x][y]:
						if shader(col, arr[x-1][y]):
							col = color_merge(col, arr[x-1][y], 1, 1)
					if  x < len(arr) - 1 and x_stride - a <= border_pix and arr[x+1][y] != arr[x][y]:
						if shader(col, arr[x+1][y]):
							col = color_merge(col, arr[x+1][y], 1, 1)
					if y > 0 and b < border_pix and arr[x][y-1] != arr[x][y]:
						if shader(col, arr[x][y-1]):
							col = color_merge(col, arr[x][y-1], 1, 1)
					if y < len(arr[0]) - 1 and y_stride - b <= border_pix and arr[x][y+1] != arr[x][y]:
						if shader(col, arr[x][y+1]):
							col = color_merge(col, arr[x][y+1], 1, 1)
				
				if do_rounding:
					m = 1
					n = (y_stride / 2) + round_radius
					p = pow(y_stride / 2, 2) / pow(x_stride/2,2)
					distance = p * pow(a-x_stride/2,2) + m * pow(b-y_stride/2,2)
					boundary = pow(n,2)
					outer_boundary = pow(n + (border_pix if do_shading else 0), 2)
					if (tl and a < x_stride / 2 and b < y_stride/2) or (bl and a < x_stride / 2 and b > y_stride/2):
							if  distance > boundary:
								if distance > outer_boundary:
									col = arr[x-1][y]
								else:
									col = color_merge(arr[x][y], arr[x-1][y], 1, 1)
					if (tr and a > x_stride / 2 and b < y_stride/2) or (br and a > x_stride / 2 and b > y_stride/2):
							if distance > boundary:
								if distance > outer_boundary:
									col = arr[x+1][y]
								else:
									col = color_merge(arr[x][y], arr[x+1][y], 1, 1)


				im.putpixel((ax, by), col)

#now insert back in removed text
if do_ocr:
	texts = get_text(filename)
	for text in texts:
		verts = text.bounding_poly.vertices
		(x, y, t) = (verts[0].x, verts[0].y, text.description)
		size = max(abs(verts[1].x - verts[0].x), abs(verts[1].x - verts[2].x), abs(verts[2].y - verts[1].y), abs(verts[1].y - verts[0].y))
		fnt = ImageFont.truetype("arial.ttf", int(2 * size/len(t)))
		# get a drawing context
		d = ImageDraw.Draw(im)
		d.text((x,y), t, font=fnt, fill=text_color)
		del d

im.save(output)

