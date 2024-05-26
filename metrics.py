import OpenEXR
import Imath
import numpy as np
import imageio
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--scene', type=str, default='cbox')
parser.add_argument('--method', type=str, default='path')
args = parser.parse_args()

name = f'{args.scene}_{args.method}'

def read_exr(file_path):
    exr_file = OpenEXR.InputFile(file_path)
    header = exr_file.header()
    dw = header['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    # Read the three color channels
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
    redstr = exr_file.channel('R', FLOAT)
    greenstr = exr_file.channel('G', FLOAT)
    bluestr = exr_file.channel('B', FLOAT)

    # Convert the byte data to numpy arrays
    red = np.frombuffer(redstr, dtype=np.float32).reshape(size[1], size[0])
    green = np.frombuffer(greenstr, dtype=np.float32).reshape(size[1], size[0])
    blue = np.frombuffer(bluestr, dtype=np.float32).reshape(size[1], size[0])

    # Stack the channels to get the final image array
    image = np.stack([red, green, blue], axis=2)
    return image

def apply_gamma_correction(image, gamma=2.2):
    """Applies gamma correction to the image."""
    return np.power(image, 1.0 / gamma)

def calculate_mse(image1, image2):
    mse = np.mean((image1 - image2) ** 2)
    return mse

def calculate_psnr(image1, image2):
    mse = calculate_mse(image1, image2)
    if mse == 0:
        return float('inf')
    max_pixel = 1.0  
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

# Paths to the EXR files
base_path = f'exr/{name}.'
label_image_path = base_path + '-1.exr'
label_image = read_exr(label_image_path)

mse_values = []
psnr_values = []
image_indices = range(1,26)

for i in image_indices:
    image_path = base_path + f'{i}.exr'
    image = read_exr(image_path)
    mse = calculate_mse(label_image, image)
    psnr = calculate_psnr(label_image, image)
    mse_values.append(mse)
    psnr_values.append(psnr)

# Plotting the MSE and PSNR curves
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(image_indices, mse_values, marker='o', linestyle='-', color='b')
plt.xlabel('Image Index')
plt.ylabel('MSE')
plt.title('MSE Curve')

plt.subplot(1, 2, 2)
plt.plot(image_indices, psnr_values, marker='o', linestyle='-', color='r')
plt.xlabel('Image Index')
plt.ylabel('PSNR (dB)')
plt.title('PSNR Curve')

plt.tight_layout()
plt.savefig(f'saved_pics/{name}_metrics.png')
