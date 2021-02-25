# coding: utf-8

import argparse
import logging
import sys
import hdr.tasks

basic_log_format = "[%(levelname)1.1s %(asctime)s.%(msecs)03dZ] [%(name)s] %(message)s"

logging.basicConfig(level=logging.INFO, format=basic_log_format)
logger = logging.getLogger(__name__)


def init_parser():
	
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-dir', help="directory of images"
    )
    parser.add_argument(
        '--output-dir', help="output dir", default='build/output'
    )
    parser.add_argument(
        '--format', help="file format", default=['.jpg']
    )
    return parser


def main():
    parser = init_parser()
    args = parser.parse_args()
    
    hdr.tasks.hdr(args.input_dir, args.format, args.output_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
