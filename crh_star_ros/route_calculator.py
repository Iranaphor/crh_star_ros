# -*- coding: utf-8 -*-
#! /usr/bin/env python3
# ----------------------------------
# @author: jheselden
# @email: jheselden@lincoln.ac.uk
# @date:
# ----------------------------------

import os, time, random

import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class RouteCalculator(Node):
    def __init__(self):
        super().__init__('speaker')
        self.map_sub = self.create_subscription(String, '/topological_map', self.tmap_cb, 10)
        self.req = self.create_subscription(String, '~request_routes', self.route_req, 10)
        self.pub = self.create_publisher(String, '~calced_routes', 10)

    def tmap_cb(self, msg):
        self.tmap = yaml.loads(msg.data)

    def route_req(self, msg):
        self.get_logger().info(msg.data)
        calc(routes)
        self.pub.publish(routes)

def main(args=None):
    rclpy.init(args=args)

    RC = Speaker()
    rclpy.spin(RC)

    RC.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
