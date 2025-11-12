import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, UnlessCondition

def generate_launch_description():

    # --- Configuration ---
    # !! Update this variable to your robot's package name !!
    # I'm using 'dexteron_prime' based on our previous conversation.
    pkg_name = 'pet2'
    
    # !! Update this to the name of your .xacro file !!
    xacro_file_name = 'robot.urdf.xacro'
    
    # !! Update this to the name of your rviz config file !!
    rviz_config_file_name = 'display.rviz'
    # ---------------------


    # 1. Declare Launch Arguments

    # Default path to the robot's xacro file
    default_model_path = PathJoinSubstitution([
        FindPackageShare(pkg_name),
        'description',
        xacro_file_name
    ])

    # Default path to the rviz config file
    default_rviz_config_path = PathJoinSubstitution([
        FindPackageShare(pkg_name),
        'rviz',
        rviz_config_file_name
    ])

    # Argument for the model
    model_arg = DeclareLaunchArgument(
        name='model',
        default_value=default_model_path,
        description='Absolute path to robot xacro file'
    )

    # Argument for the rviz config
    rviz_config_arg = DeclareLaunchArgument(
        name='rvizconfig',
        default_value=default_rviz_config_path,
        description='Absolute path to Rviz config file'
    )

    # Argument for launching the GUI
    gui_arg = DeclareLaunchArgument(
        name='gui',
        default_value='true',
        description='Flag to enable/disable joint_state_publisher_gui',
        choices=['true', 'false']
    )

    # 2. Process Robot Description (Xacro to URDF)
    robot_description_content = Command([
        'xacro ', 
        LaunchConfiguration('model')
    ])

    # 3. Define Nodes

    # Robot State Publisher
    # This node reads the URDF from the 'robot_description' parameter
    # and publishes the /tf and /tf_static topics.
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    # Joint State Publisher (GUI)
    # This node publishes the /joint_states topic, which is read by
    # robot_state_publisher. It provides a GUI with sliders.
    # It is only launched if the 'gui' argument is 'true'.
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('gui'))
    )
    
    # Joint State Publisher (non-GUI)
    # This node publishes default /joint_states (all zeros).
    # It is launched if the 'gui' argument is 'false'.
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )

    # Rviz2 Node
    # This node opens Rviz2 and loads the config file specified
    # by the 'rvizconfig' launch argument.
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')]
    )

    # 4. Assemble Launch Description
    return LaunchDescription([
        # Add launch arguments
        model_arg,
        rviz_config_arg,
        gui_arg,
        
        # Add nodes to run
        joint_state_publisher_gui_node,
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node
    ])