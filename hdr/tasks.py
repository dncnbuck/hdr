import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import os
import logging


logger = logging.getLogger(__name__)


def get_images_in_dir(input_dir, import_formats=None):
  image_files = []
  import_formats = ['.jpg']

  logger.info("Reading Images in {} of type {}".format(input_dir, import_formats))
  for f in os.listdir(input_dir):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in import_formats:
        continue
    image_files.append(os.path.join(input_dir, f))
  return image_files

def read_images(image_files):
  images = []
  for f in image_files:
    im = cv2.imread(f)
    images.append(im)
  return images


def save_image(file_path, image):
  if not os.path.exists(os.path.dirname(file_path)):
    os.makedirs(os.path.dirname(file_path))
  cv2.imwrite(file_path, image)
  logger.info("saved {}".format(file_path))


def align_images(images):
  # Align input images
  logger.info("Aligning images ... ")
  alignMTB = cv2.createAlignMTB()
  alignMTB.process(images, images)


def get_image_exposures(image_files):
  exposure_times = []
  for f in image_files:
    im_pil = Image.open(f)
    exifdata = im_pil.getexif()
    exif_data = {}
    # iterating over all EXIF data fields
    for tag_id in exifdata:
      # get the tag name, instead of human unreadable tag id
      tag = TAGS.get(tag_id, tag_id)
      data = exifdata.get(tag_id)
      exif_data[tag] = data
    
    exposure_times.append(exif_data['ExposureTime'])
    
  # Should read images and get metadata and extract image exposure times
  return np.array(exposure_times, dtype=np.float32)


def get_camera_reponse_function(images, times):
  # Obtain Camera Response Function (CRF)
  logger.info("Calculating Camera Response Function (CRF) ... ")
  calibrateDebevec = cv2.createCalibrateDebevec()
  responseDebevec = calibrateDebevec.process(images, times)
  return responseDebevec


def merge_image_to_hdr(images, times, responseDebevec):
  # Merge images into an HDR linear image
  logger.info("Merging images into one HDR image ... ")
  mergeDebevec = cv2.createMergeDebevec()
  hdrDebevec = mergeDebevec.process(images, times, responseDebevec)
  return hdrDebevec
  

def hdr(input_dir, import_formats, output_dir):

  # Find Image Files
  image_files = get_images_in_dir(input_dir, import_formats)
  # Load images
  images = read_images(image_files)
  # Read Exposure times
  times = get_image_exposures(image_files)
  # Align input images
  align_images(images)
  # Obtain Camera Response Function (CRF)
  responseDebevec = get_camera_reponse_function(images, times)
  # Merge images into an HDR linear image
  hdrDebevec = merge_image_to_hdr(images, times, responseDebevec)
  # Save HDR image.
  save_image(file_path=os.path.join(output_dir, input_dir, "hdrDebevec.hdr"), image=hdrDebevec)
  # Save tonemapped images
  methods = ['drago', 'reinhard', 'mantiuk']
  for method in methods:
    image = generate_tonemap(hdrDebevec, method)
    save_image(file_path=os.path.join(output_dir, input_dir, "ldr-{}.jpg".format(method)), image=image * 255)


def generate_tonemap(hdr_image, method):
  if method == 'drago':
    image = tonemap_drago(hdr_image)
  elif method == 'reinhard':
    image = tonemap_reinhard(hdr_image)
  elif method == 'mantiuk':
    image = tonemap_mantiuk(hdr_image)
  return image


def tonemap_drago(hdr_image):
  # Tonemap using Drago's method to obtain 24-bit color image
  logger.info("Tonemaping using Drago's method ... ")
  tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
  ldrDrago = tonemapDrago.process(hdr_image)
  ldrDrago = 3 * ldrDrago
  return ldrDrago


def tonemap_reinhard(hdr_image):
  # Tonemap using Drago's method to obtain 24-bit color image
  logger.info("Tonemaping using Reinhard's method ... ")
  tonemapReinhard = cv2.createTonemapReinhard(1.5, 0,0,0)
  ldrReinhard = tonemapReinhard.process(hdr_image)
  return ldrReinhard


def tonemap_mantiuk(hdr_image):
  # Tonemap using Mantiuk's method to obtain 24-bit color image
  logger.info("Tonemaping using Mantiuk's method ... ")
  tonemapMantiuk = cv2.createTonemapMantiuk(2.2,0.85, 1.2)
  ldrMantiuk = tonemapMantiuk.process(hdr_image)
  ldrMantiuk = 3 * ldrMantiuk
  return ldrMantiuk


