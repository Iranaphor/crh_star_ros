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

from crh_star_ros.planner import plan


class RouteCalculator(Node):
    def __init__(self):
        super().__init__('route_calculator')
        self.map_sub = self.create_subscription(String, '/topological_map', self.tmap_cb, 10)
        self.loc_sub = self.create_subscription(String, '/rasberry_coordination/fleet_monitoring/fleet', self.tmap_cb, 10)
        self.req = self.create_subscription(String, '~request_routes', self.route_req, 10)
        self.pub = self.create_publisher(String, '~calculated_routes', 10, latch=True)

    def tmap_cb(self, msg):
        self.tmap = yaml.loads(msg.data)

        # Create a reservation table for each node, and for each edge
        for node in self.tmap['nodes']:
            node['reservation_table'] = None

            for edge in node['edges']:
                edge['reservation_table'] = None

    def route_req(self, msg):
        if not self.tmap:
            self.get_logger().info('map not initialised')
            return
        self.get_logger().info(msg.data)
        routes = plan(msg)
        self.pub.publish(routes)


def main(args=None):
    rclpy.init(args=args)

    RC = RouteCalculator()
    rclpy.spin(RC)

    RC.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
