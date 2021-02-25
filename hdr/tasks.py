import cv2
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)


def read_images(input_dir, import_formats=None):
  images = []
  import_formats = ['.jpg']

  logger.info("Reading Images in {} of type {}".format(input_dir, import_formats))
  for f in os.listdir(input_dir):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in import_formats:
        continue
    logger.info(f)
    im = cv2.imread(os.path.join(input_dir,f))
    images.append(im)
  return images


def save_image(file_path, image):
  if not os.path.exists(os.path.dirname(file_path)):
    os.mkdir(os.path.dirname(file_path))
  cv2.imwrite(file_path, image)
  logger.info("saved {}".format(file_path))


def align_images(images):
  # Align input images
  logger.info("Aligning images ... ")
  alignMTB = cv2.createAlignMTB()
  alignMTB.process(images, images)


def get_image_exposures(images):
  # Should read images and get metadata and extract image exposure times
  return np.array([ 1/30.0, 2.5, 15.0, 0.25, ], dtype=np.float32)


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

  # Load images
  images = read_images(input_dir, import_formats)
  # Read Exposure times
  times = get_image_exposures(images)
  # Align input images
  align_images(images)
  # Obtain Camera Response Function (CRF)
  responseDebevec = get_camera_reponse_function(images, times)
  # Merge images into an HDR linear image
  hdrDebevec = merge_image_to_hdr(images, times, responseDebevec)
  # Save HDR image.
  save_image(file_path=os.path.join(output_dir,"hdrDebevec.hdr"), image=hdrDebevec)
  # Save tonemapped images
  methods = ['drago', 'reinhard', 'mantiuk']
  for method in methods:
    image = generate_tonemap(hdrDebevec, method)
    save_image(file_path=os.path.join(output_dir, "ldr-{}.jpg".format(method)), image=image * 255)


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


