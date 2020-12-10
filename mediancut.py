import operator
from PIL import Image
import numpy as np


def sort_group(mode, arr_list):
    arr_list.sort(key=operator.itemgetter(mode))
    return arr_list


def half_cut(array_list):
    return array_list[0:len(array_list) // 2], array_list[len(array_list) // 2:]


def get_mean(array_list):
    return np.mean(array_list, axis=0, dtype=np.int32).tolist()


def find_distance(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    return (x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2


def main_func(array_list, depth, fin_block):
    temp_list = array_list.copy()
    if depth == 8:
        fin_block.append(temp_list)
        return
    # find the distinct value of r g and b
    set_r = set()
    set_g = set()
    set_b = set()
    for r, g, b in array_list:
        set_r.add(r)
        set_g.add(g)
        set_b.add(b)
    # whichever value is maximam use the appropriate value of mode in sort_group(mode=0 for r, 1 for r...)
    distinct_count_list = [len(set_r), len(set_g), len(set_b)]
    mode = distinct_count_list.index(max(distinct_count_list))
    temp_list2 = sort_group(mode, temp_list)
    left, right = half_cut(temp_list2)
    main_func(left, depth + 1, final_block)
    main_func(right, depth + 1, final_block)


def creat_lut(final_block_var):
    final_lut = []
    for block in final_block_var:
        final_lut.append(get_mean(block))
    return final_lut


def euclidien_dis(pixel, final_lut):
    all_distance = [find_distance(pixel, entry) for entry in final_lut]
    return np.argmin(all_distance)


def reduce_image(array_list, final_lut):
    array_list2 = [euclidien_dis(pixel, final_lut) for pixel in array_list]
    return array_list2


def generate_lut(list1):
    res = []
    for i in list1:
        res.append(i[0])
        res.append(i[1])
        res.append(i[2])
    return res


image1 = Image.open("peppers.tif")
# image1.show()
array_list_final = list(image1.getdata())
# print(image1.size)
# print(array_list_final)

final_block = []
main_func(array_list_final, 0, final_block)
final_look_up_table = []
final_look_up_table = creat_lut(final_block)
palette_map = generate_lut(final_look_up_table)

csv_data = [["Index", "R","G","B"]]
for index,val in enumerate(final_look_up_table):
    csv_data.append([index,val[0],val[1],val[2]])

np.savetxt("palette.csv", csv_data, delimiter=",", fmt='%s' )

new_p_image = Image.new(mode="P", size=(512, 512))
for i in range(512):
    for j in range(512):
        index_val = euclidien_dis(array_list_final[512 * i + j], final_look_up_table)
        new_p_image.putpixel((j, i), int(index_val))
new_p_image.putpalette(palette_map)
new_p_image.save("peppers-8.tif")
new_p_image.show()
