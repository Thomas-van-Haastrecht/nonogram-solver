__author__ = "Thomas van Haastrecht"
__credits__ = ["Thomas van Haastrecht"]

from PIL import Image, ImageDraw, ImageFont

GRIDSIZE = 50
LINESIZE = 2
CHARWIDTH = 64

mark_img = Image.open('display-files/mark.png', 'r')
cross_img = Image.open('display-files/cross.png', 'r')

font = ImageFont.truetype(font='display-files/JAi_____.ttf', size=64)
large_font = ImageFont.truetype(font='display-files/JAi_____.ttf', size=44)


def display_grid(array, row, column):
    rows = array.shape[0]
    columns = array.shape[1]
    height = rows * GRIDSIZE + (rows + 1) * LINESIZE + (rows // 5)
    width = columns * GRIDSIZE + (columns + 1) * LINESIZE + (columns // 5)

    set_len = [len(r) for r in row]
    set_len.extend([len(c) for c in column])
    m = max(set_len)

    img = Image.new('RGB', (width + m*CHARWIDTH, height + m*CHARWIDTH), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # draw grid - missing top row rn
    count_x = 0
    count_y = 0
    t_line = 0
    # draw vertical lines
    while count_x < height:
        if t_line < len(column):
            # add in nums
            for n in range(len(column[t_line])):
                x = (m + 0.1) * CHARWIDTH + count_x
                y = (m - n -1) * CHARWIDTH
                num = column[t_line][-1-n]
                if num >= 10:
                    draw.text((x-7, y+10), str(num), font=large_font, fill=(0, 0, 0))
                else:
                    draw.text((x, y), str(num), font=font, fill=(0, 0, 0))

        if t_line % 5 == 0:
            draw.line([count_x + m*CHARWIDTH, 0 + m*CHARWIDTH, count_x + m*CHARWIDTH, width + m*CHARWIDTH], fill='black', width=LINESIZE+1)
            count_x += GRIDSIZE + LINESIZE + 1

        else:
            draw.line([count_x + m*CHARWIDTH, 0 + m*CHARWIDTH, count_x + m*CHARWIDTH, width + m*CHARWIDTH], fill='black', width=LINESIZE)
            count_x += GRIDSIZE + LINESIZE
        t_line += 1
    t_line = 0

    while count_y < width:
        if t_line < len(row):
            # add in nums
            for n in range(len(row[t_line])):
                x = (m - n - 1) * CHARWIDTH
                y = m * CHARWIDTH + count_y
                num = row[t_line][-1-n]
                if num >= 10:
                    draw.text((x-7, y+10), str(num), font=large_font, fill=(0, 0, 0))
                else:
                    draw.text((x, y), str(num), font=font, fill=(0, 0, 0))

        if t_line % 5 == 0:
            draw.line([0 + m*CHARWIDTH, count_y + m*CHARWIDTH, height + m*CHARWIDTH, count_y + m*CHARWIDTH], fill='black', width=LINESIZE + 1)
            count_y += GRIDSIZE + LINESIZE + 1
        else:
            draw.line([0 + m*CHARWIDTH, count_y + m*CHARWIDTH, height + m*CHARWIDTH, count_y + m*CHARWIDTH], fill='black', width=LINESIZE)
            count_y += GRIDSIZE + LINESIZE
        t_line += 1

    # add marks and crosses to image

    for i in range(rows):
        for j in range(columns):
            x_off = m*CHARWIDTH + GRIDSIZE * i + LINESIZE * (i + 1) + i // 5 + 2
            y_off = m*CHARWIDTH + GRIDSIZE * j + LINESIZE * (j + 1) + j // 5 + 2
            offset = (x_off, y_off)
            if array[j][i] == 1:
                img.paste(mark_img, offset)
            elif array[j][i] == -1:
                img.paste(cross_img, offset)
            # im_draw(img, i, j, array[j][i])

    img.show()
    return img
