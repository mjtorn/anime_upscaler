import torch
import torchvision
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import cv2
import argparse
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import image_slicer
from image_slicer import join
from PIL import Image
import numpy as np

def upscale(model_path, im_path):
	model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
	upsampler = RealESRGANer(scale=4, model_path=model_path, model=model, tile=0, tile_pad=10, pre_pad=0, half=False)
	img = cv2.imread(im_path, cv2.IMREAD_UNCHANGED)
	output, _ = upsampler.enhance(img, outscale=4)
	return output


def upscale_slice(model_path, image, slice):
	width, height = Image.open(image).size
	tiles = image_slicer.slice(image, slice, save=False)
	model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
	upsampler = RealESRGANer(scale=4, model_path=model_path, model=model, tile=0, tile_pad=10, pre_pad=0, half=False)
	for tile in tiles:
		output, _ = upsampler.enhance(np.array(tile.image), outscale=4)
		tile.image = Image.fromarray(output)
		tile.coords = (tile.coords[0]*slice, tile.coords[1]*slice)
	return join(tiles, width=width*slice, height=height*slice)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-m', '--model_path', type=str, help='REQUIRED: specify path of the model being used')
	parser.add_argument('-i', '--input', type=str, help='REQUIRED: specify path of the image you want to upscale')
	parser.add_argument('-o', '--output', type=str, help='REQUIRED: specify path where you want to save image')
	parser.add_argument('-v', '--visualize', action='store_true', help='OPTIONAL: add this to see how image looks before and after upscale')
	parser.add_argument('-s', '--slice', nargs='?', type=int, const=4, help='OPTIONAL: specify weather to split frames, recommended to use to help with VRAM unless you got a fucken quadro or something' )
	args = parser.parse_args()

	if args.model_path and args.input and args.output:
		if args.slice:
			output = upscale_slice(args.model_path, args.input, args.slice)
			output.save(args.output)
		else:
			output = upscale(args.model_path, args.input)
			cv2.imwrite(args.output, output)
		if args.visualize:
			plt.imshow(mpimg.imread(args.input))
			plt.show()
			plt.imshow(output)
			plt.show()
	else:
		print('Error: Missing arguments, check -h, --help for details')


			# tiles = image_slicer.slice('tmp/{}/original/{}'.format(folder_name, i), slice, save=False)
			# print(tiles)
			# for tile in tiles:
			# 	up = frame_esrgan.upscale_slice(args.model_path, np.array(tile.image))
			# 	tile.image = Image.fromarray(up, 'RGB')
			# out = join(tiles)
			# out.save('tmp/{}/upscaled/{}'.format(folder_name, i.replace('jpg', 'png')))
