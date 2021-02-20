#!/usr/bin/env python3

import csv
from pprint import pprint
import argparse
import numpy as np
import matplotlib.pyplot as plt
import os

def load_map(nem_path):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="path to input csv file or directory")
    parser.add_argument("--x_index", help="column index of position x", default=5)
    parser.add_argument("--y_index", help="column index of position y", default=6)
    parser.add_argument("--x_min", help="left", default=-200, type=float)
    parser.add_argument("--x_max", help="right", default=200, type=float)
    parser.add_argument("--y_min", help="up", default=-350, type=float)
    parser.add_argument("--y_max", help="down", default=50, type=float)
    parser.add_argument("--offset", help="enable offset", action='store_true')
    parser.add_argument("--save", help="save flag", action='store_true')
    args = parser.parse_args()

    colors = ["red", "cyan", "gray", "green"]
    zorder = [4, 2, 1, 3]

    file_names = []
    if os.path.isdir(args.input):
        for file_name in os.listdir(args.input):
            # file_names.append(os.path.basename(args.input) + "/" + file_name)
            file_names.append(args.input + "/" + file_name)
    else:
        file_names.append(args.input)

    print(file_names)
    # plot
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['font.size'] = '18'
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0, right=1, bottom=0.15, top=0.95)
    ax.set_xlabel('x[m]')
    ax.set_ylabel('y[m]')
    ax.set_aspect('equal')


    # load data from file
    for i, file_name in enumerate(file_names):
        data = None
        print(file_name)
        with open(file_name) as f:
            reader = csv.reader(f)
            data = [row for row in reader]

        data = np.array(data)

        # extract data
        x_data = data[1:, args.x_index]
        x_data = [float(v) for v in x_data]
        x_data = np.array(x_data)
        y_data = data[1:, args.y_index]
        y_data = [float(v) for v in y_data]
        y_data = np.array(y_data)

        if not args.offset:
            ax.set_xlim(args.x_min, args.x_max)
            ax.set_ylim(args.y_min, args.y_max)
        else:
            ax.set_xlim(0, args.x_max - args.x_min)
            ax.set_ylim(0, args.y_max - args.y_min)
            x_data = x_data - args.x_min
            y_data = y_data - args.y_min
        ax.plot(x_data, y_data, c=colors[i], linewidth=1.0, zorder=zorder[i])

    # ax.grid()
    plt.tight_layout()

    if not args.save:
        plt.show()
    else:
        plt.savefig('test.png', bbox_inches="tight", dpi=300)
        print("saved")
