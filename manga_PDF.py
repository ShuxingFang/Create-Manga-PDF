import subprocess
import os
import sys
import img2pdf
import shutil
import cv2
#The plan is to make this the ultimate one step PDF manga maker

# Step 1: delete any png in the folder
def delete_png(directory):
    files = os.listdir(directory)
    png_files = [f for f in files if f.endswith('.png')and not f.startswith('._')]
    if len(png_files) == 1:
        os.remove(os.path.join(directory, png_files[0]))

# Step 2: start to combine every two pictures into a single one, with their order reversed
def merge_images(directory):
    images = [f for f in os.listdir(directory) if (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg')) and not f.startswith('._')]
    images.sort()

    cover_num = int(sys.argv[2])
    temp = os.path.join(directory, 'temporary')
    os.makedirs(temp, exist_ok=True)

    jpeg_quality = 95  # Set JPEG quality here

    for i in range(cover_num):
        image_path = os.path.join(directory, images[i])
        img = cv2.imread(image_path)
        cv2.imwrite(os.path.join(temp, f'{i}.jpg'), img, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])

    counter = cover_num
    i = cover_num

    while i < len(images):
        img1_path = os.path.join(directory, images[i])
        img1 = cv2.imread(img1_path)

        if img1.shape[1] > img1.shape[0]:  # Width > Height
            new_img_name = f'{counter:d}.jpg'
            counter += 1
            new_img_path = os.path.join(temp, new_img_name)
            cv2.imwrite(new_img_path, img1, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
            i += 1
            continue

        if i + 1 < len(images):
            img2_path = os.path.join(directory, images[i + 1])
            img2 = cv2.imread(img2_path)

            if img1.shape[0] != img2.shape[0]:  # If heights differ
                new_height = max(img1.shape[0], img2.shape[0])
                img1 = cv2.resize(img1, (img1.shape[1], new_height))
                img2 = cv2.resize(img2, (img2.shape[1], new_height))

            merged = cv2.hconcat([img2, img1])

            output_filename = f'{counter:d}.jpg'
            counter += 1
            cv2.imwrite(os.path.join(temp, output_filename), merged, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])

        elif i == len(images) - 1:
            last_img_path = os.path.join(directory, images[i])
            new_last_img_name = f'{counter:d}.jpg'
            counter += 1
            new_last_img_path = os.path.join(temp, new_last_img_name)
            img = cv2.imread(last_img_path)
            cv2.imwrite(new_last_img_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])

        i += 2



# Step 3 Merge the jpg we generated into PDF
def images_to_pdf(directory):
    images = [f for f in os.listdir(directory)]
    images.sort(key=lambda x: int(x.split('.')[0]))
    images = [os.path.join(directory, f) for f in images]
    abs_path = os.path.abspath(directory)
    name = os.path.basename(os.path.dirname(abs_path))
    output_folder = '/Users/shuxingfang/Downloads'
    pdf_filename = os.path.join(output_folder, f'{name}.pdf')

    try:
        with open(pdf_filename, "wb") as f:
            f.write(img2pdf.convert(images))
    except Exception as e:
        print(f"An error occurred: {e}")

# Step 4 Job is done! time to send a notification!
def notify(directory):
    folder_name = os.path.basename(directory)
    notification_title = "Yay!"
    notification_text = f'{folder_name} is done merging'

    subprocess.run([
        'osascript',
        '-e',
        f'display notification "{notification_text}" with title "{notification_title}"'
    ])

# main function of the program
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python merge_images.py <path_to_your_images_directory> <number_of_covers>")
    else:
        directory = sys.argv[1]
        cover_num = int(sys.argv[2])
        temp = os.path.join(directory, 'temporary')
        os.makedirs(temp, exist_ok=True)

        delete_png(directory)
        merge_images(directory)
        images_to_pdf(temp)
        shutil.rmtree(temp)
        notify(directory)
