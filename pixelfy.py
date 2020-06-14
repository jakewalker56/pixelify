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

sys.argv
if len(sys.argv) > 1:
	x_stride = int(sys.argv[1])
else:
	x_stride = 30

if len(sys.argv) > 2:
	y_stride = int(sys.argv[2])
else:
	y_stride = 30

if len(sys.argv) > 3:
	shift = float(sys.argv[3])
else:
	shift = 0.5

if len(sys.argv) > 4:
	clusters = int(sys.argv[4])
else:
	clusters = 6
border_pix = 0 #int((x_stride + y_stride) / 20)
round_radius = y_stride / 2.2
do_rounding = True
do_shading = True
#
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def shader(col1, col2):
	return max(col1[0], col1[1], col1[2]) > max(col2[0], col2[1], col2[2])

def color_merge(col1, col2, str1, str2):
	return (int((str1 * col1[0] + str2*col2[0]) / (str1 + str2)), int((str1 * col1[1] + str2*col2[1]) / (str1 + str2)), int((str1 * col1[2] + str2*col2[2]) / (str1 + str2)), 255)

# def get_text(im):

#     client = vision.ImageAnnotatorClient()
#     flattened = list(itertools.chain(*list(im.getdata())))
#     image = vision.types.Image(content=bytes(flattened))
#     response = client.text_detection(image=image)
#     texts = response.text_annotations
#     print('Texts:')

#     for text in texts:
#         print('\n"{}"'.format(text.description))
#         vertices = (['({},{})'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])

#         print('bounds: {}'.format(','.join(vertices)))

#     if response.error.message:
#         raise Exception(
#             '{}\nFor more info on error messages, check: '
#             'https://cloud.google.com/apis/design/errors'.format(
#                 response.error.message))

for filename in ["image11.png","image.png", "image2.png", "image3.png", "image4.png"]: #,"image5.png", "image6.png", "image7.png", "image8.png", "image10.png"]:
	im = Image.open(filename)
	#get_text(im)
	
	# d = pytesseract.image_to_data(im, output_type=pytesseract.Output.DICT)
	# conf_threshold = np.array(list(map(int, d['conf']))) > 60
	# text = np.array(d['text'])[conf_threshold]
	# left = np.array(d['left'])[conf_threshold]
	# top = np.array(d['top'])[conf_threshold]
	# boxwidth = np.array(d['width'])[conf_threshold]
	# boxheight = np.array(d['height'])[conf_threshold]
	
	#automatic
	#im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
	#im = im.quantize(colors=100, method=None, kmeans=0, palette=None)
	#im = im.quantize(colors=50, method=None, kmeans=0, palette=None)

	#manual
	#given_value = 2
	#a_list = [1, 5, 8]
	#closest_value = min(a_list, key=absolute_difference_function)
	#print(closest_value)


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
			#TODO: implement voting instead of averaging to deal with complex scenery
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
						n = 2 * (y_stride / 2) - round_radius
						p = pow(y_stride / 2, 2) / pow(x_stride/2,2)
						distance = p * pow(a-x_stride/2,2) + m * pow(b-y_stride/2,2)
						boundary = pow(n,2)
						outer_boundary = pow(n+border_pix, 2)
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
	#TODO: try google cloud vision API
	# print(text)
	# n_boxes = len(text)
	# for i in range(n_boxes):
	# 	(x, y, w, h, t) = (left[i], top[i], boxwidth[i], boxheight[i], text[i])
	# 	if w > 5 and h > 5:
	# 		fnt = ImageFont.truetype("arial.ttf", int(h/2))
	# 		# get a drawing context
	# 		d = ImageDraw.Draw(im)
	# 		d.text((x,y), t, font=fnt, fill=(0,0,0,255))
	# 		del d
	    

	im.show()

