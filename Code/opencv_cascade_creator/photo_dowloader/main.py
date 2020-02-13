""" Kuwin Wyke
Midwestern State University

This program downloads negative images and creates a text file specifying the
location of the images using a relative path.
"""

from make_negatives import download_negatives_and_create_text_file


def main():
    download_negatives_and_create_text_file(
        output_name="negatives_main_thread"
    )


if __name__ == '__main__':
    main()
