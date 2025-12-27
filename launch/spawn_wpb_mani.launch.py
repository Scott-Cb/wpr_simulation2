#!/usr/bin/env python3
#
# Copyright 2023 6-robot.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Zhang Wanjie

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.event_handlers import OnProcessExit
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():
    # Use the SDF model file directly for spawning in Gazebo
    model_path = os.path.join(
        get_package_share_directory('wpr_simulation2'),
        'models',
        'wpb_home_mani.model'
    )
    

    # Launch configuration variables specific to simulation
    pose_x = LaunchConfiguration('pose_x', default='0.0')
    pose_y = LaunchConfiguration('pose_y', default='0.0')
    pose_theta = LaunchConfiguration('pose_theta', default='0.0')

    # Declare the launch arguments (names match LaunchConfiguration above)
    declare_x_position_cmd = DeclareLaunchArgument(
        'pose_x', default_value='0.0',
        description='Specify x position of the robot')

    declare_y_position_cmd = DeclareLaunchArgument(
        'pose_y', default_value='0.0',
        description='Specify y position of the robot')

    declare_load_controllers = DeclareLaunchArgument(
        'load_controllers', default_value='true',
        description='Whether to load ros2_control controllers')

    start_gazebo_ros_spawner_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-file', model_path,
            '-entity', 'wpb_home_mani',
            '-x', pose_x,
            '-y', pose_y,
            '-Y', pose_theta
        ],
        output='screen',
    )

    load_joint_state_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )

    load_manipulator_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'manipulator_controller'],
        output='screen'
    )

    wpb_home_mani_sim = Node(
            package='wpr_simulation2',
            executable='wpb_home_mani_sim',
            name='wpb_home_mani_sim',
            output='screen'
        )

    return LaunchDescription([
        declare_x_position_cmd,
        declare_y_position_cmd,
        declare_load_controllers,
        RegisterEventHandler(
            condition=IfCondition(LaunchConfiguration('load_controllers')),
            event_handler=OnProcessExit(
                target_action=start_gazebo_ros_spawner_cmd,
                on_exit=[load_joint_state_controller],
            )
        ),
        RegisterEventHandler(
            condition=IfCondition(LaunchConfiguration('load_controllers')),
            event_handler=OnProcessExit(
                target_action=load_joint_state_controller,
                on_exit=[load_manipulator_controller],
            )
        ),
        RegisterEventHandler(
            condition=IfCondition(LaunchConfiguration('load_controllers')),
            event_handler=OnProcessExit(
                target_action=load_manipulator_controller,
                on_exit=[wpb_home_mani_sim],
            )
        ),
        # control_node,
        # joint_state_publisher_node,
        start_gazebo_ros_spawner_cmd,
    ])
