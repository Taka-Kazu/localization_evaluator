#!/usr/bin/env python3

import csv
from pprint import pprint
import argparse
import numpy as np
import matplotlib.pyplot as plt
import os

from geometry_msgs.msg import Quaternion
from tf.transformations import euler_from_quaternion, quaternion_from_euler

def load_map(nem_path):
    pass

def get_yaw(qx, qy, qz, qw):
    return np.arctan2(2*(qw*qz+qx*qy), 1-2*(qy**2+qz**2))

def compute_error(a, b):
    count = 0
    sum_xy = 0
    sum_yaw = 0
    dxy_list = []
    dyaw_list = []
    t_list = []
    for i, row in enumerate(a):
        index = np.where(b[:, 0] == row[0])[0]
        if index.size > 0:
            index = index[0]
            xy0 = row[1:3]
            xy1 = b[index][1:3]
            d = np.linalg.norm(xy0 - xy1)
            sum_xy = sum_xy + d**2
            yaw0 = row[3]
            yaw1 = b[index][3]
            dyaw = yaw0 - yaw1
            dyaw = np.arctan2(np.sin(dyaw), np.cos(dyaw))
            sum_yaw = sum_yaw + dyaw**2
            dxy_list.append(d)
            dyaw_list.append(dyaw)
            t_list.append(row[0])
            count = count + 1
    dxy_list = np.array(dxy_list)
    t_list = np.array(t_list) * 1e-9
    t_list = t_list - t_list[0]
    return count, sum_xy, sum_yaw, dxy_list, dyaw_list, t_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("input", help="path to input csv file or directory")
    parser.add_argument("file0", help="path to input csv file")
    parser.add_argument("file1", help="path to input csv file")
    parser.add_argument("--file2", help="path to input csv file", default=None)
    parser.add_argument("--stamp_index", help="column index of time stamp", default=2)
    parser.add_argument("--x_index", help="column index of position x", default=5)
    parser.add_argument("--y_index", help="column index of position y", default=6)
    parser.add_argument("--qx_index", help="column index of orientation x", default=8)
    parser.add_argument("--ori", help="evaluate orientation", action='store_true')
    parser.add_argument("--save", help="save flag", action='store_true')
    args = parser.parse_args()

    colors = ["red", "gray", "blue", "green"]

    file_names = [args.file0, args.file1]
    if args.file2:
        file_names.append(args.file2)

    print(file_names)
    # plot
    # plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['font.size'] = '12'
    plt.rcParams["legend.fancybox"] = False
    plt.rcParams["legend.edgecolor"] = 'black'
    plt.rcParams["legend.framealpha"] = 1

    fig, ax = plt.subplots()
    ax.set_xlabel('t[s]')
    ax.set_xlim(0, 1000)
    if not args.ori:
        ax.set_ylabel('Positional error[m]')
        ax.set_ylim(0, 10)
    else:
        ax.set_ylabel('Orientational error[rad]')
        ax.set_ylim(0, 0.3)
    # ax.set_aspect('equal')

    v = []

    # load data from file
    for i, file_name in enumerate(file_names):
        data = None
        print(file_name)
        with open(file_name) as f:
            reader = csv.reader(f)
            data = [row for row in reader]

        data = np.array(data)

        # extract data
        t_data = data[1:, args.stamp_index]
        t_data = [float(v) for v in t_data]
        t_data = np.array(t_data).reshape(-1, 1)
        x_data = data[1:, args.x_index]
        x_data = [float(v) for v in x_data]
        x_data = np.array(x_data).reshape(-1, 1)
        y_data = data[1:, args.y_index]
        y_data = [float(v) for v in y_data]
        y_data = np.array(y_data).reshape(-1, 1)
        qx_data = data[1:, args.qx_index]
        qx_data = [float(v) for v in qx_data]
        qx_data = np.array(qx_data)
        qy_data = data[1:, args.qx_index+1]
        qy_data = [float(v) for v in qy_data]
        qy_data = np.array(qy_data)
        qz_data = data[1:, args.qx_index+2]
        qz_data = [float(v) for v in qz_data]
        qz_data = np.array(qz_data)
        qw_data = data[1:, args.qx_index+3]
        qw_data = [float(v) for v in qw_data]
        qw_data = np.array(qw_data)
        yaw_data = get_yaw(qx_data, qy_data, qz_data, qw_data).reshape(-1, 1)
        p = np.hstack((t_data, x_data, y_data, yaw_data))
        # print(p[:3])
        print(p.shape)
        v.append(p)

    print(v[0].shape)

    count, sum_xy, sum_yaw, dxy_list, dyaw_list, t_list = compute_error(v[0], v[1])

    print("count: ", count)
    print("RMSE pos: ", np.sqrt(sum_xy/float(count)))
    print("RMSE ori: ", np.sqrt(sum_yaw/float(count)))

    print("max pos error: ", np.max(dxy_list))
    print("min pos error: ", np.min(dxy_list))
    print("max error time: ", t_list[np.argmax(dxy_list)])
    print("max ori error: ", np.max(dyaw_list))
    print("min ori error: ", np.min(dyaw_list))
    print("max error time: ", t_list[np.argmax(dyaw_list)])

    if not args.ori:
        ax.plot(t_list, dxy_list, linewidth=1.0, label="Proposed method", color="red")
    else:
        ax.plot(t_list, dyaw_list, linewidth=1.0, label="Proposed method", color="red")

    if args.file2:
        count2, sum_xy2, sum_yaw2, dxy_list2, dyaw_list2, t_list2 = compute_error(v[0], v[2])
        if not args.ori:
            ax.plot(t_list2, dxy_list2, linewidth=1.0, label="Previous method", color="green")
        else:
            ax.plot(t_list2, dyaw_list2, linewidth=1.0, label="Previous method", color="green")

    ax.grid()
    ax.legend()
    plt.tight_layout()

    plt.show()
    if not args.save:
        plt.show()
    else:
        plt.savefig('test.png', bbox_inches="tight")
        print("saved")
