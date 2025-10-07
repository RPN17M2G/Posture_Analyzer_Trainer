# Pose Trainer Prototype

**This application is a PROTOTYPE and not yet fully developed or optimized for production use.**

Pose Trainer is a prototype Python application for **real-time posture and movement feedback**.
It compares your body position and joint angles to a reference video and provides immediate visual guidance, making it useful for **training, dance practice, sports performance, or improving presentation posture**. By seeing exactly where your joints are misaligned or how to match a target position, you can train more effectively and correct movements in real time.

## Reference Extraction

The system can analyze any video and extract:

* **Joint angles** — such as elbows, shoulders, knees, and neck.
* **Normalized joint coordinates** — allowing consistent comparison across different camera sizes or user positions.

All extracted data is saved as a `.csv` file, which can be reused for comparisons with live webcam input. This allows the reference video to serve as a standard for training or choreography, so the user can match their movements to the target.

## Live Posture Trainer

The live trainer uses your webcam to detect your pose in real time and compare it to the reference data. It provides **two visual feedback modes** and displays the reference video alongside your webcam feed for easier comparison:

### Mode 1 (User Feedback)
  Displays your skeleton with lines colored according to alignment:

  * **Green lines** indicate joints that match the reference position.
  * **Red lines** indicate misaligned joints.
    This mode gives **direct feedback on your current posture**, helping you adjust in real time.

### Mode 2 (Reference Only)
  Overlays a scaled reference skeleton on your webcam feed so you can visually align yourself to the target posture.
  The reference video is sshown alongside your camera feed, so you can **see the target movement and match it precisely**.

Switch between modes by pressing **M**, and press **Q** to quit the application.

## The Thinking Behind Joint Angles

One of the key ideas behind this system is **using joint angles instead of absolute positions**.

People have different body proportions(For example: arm length, leg length, or overall height) but the **relative angles between joints remain consistent** when performing the same movement. For example, even if one person has longer arms than another, a fully extended arm still forms the **same elbow angle**, regardless of the hand's absolute position in space. This makes **angles a robust metric for posture and motion comparison**.

Mathematically, for a joint B connected to points A and C:

$
\theta = \arccos \left( \frac{\vec{BA} \cdot \vec{BC}}{|\vec{BA}| , |\vec{BC}|} \right)
$

Where:

* ($\vec{BA}$) is the vector from B to A
* ($\vec{BC}$) is the vector from B to C
* ($\theta$) is the angle at joint B

Because this uses the **relative direction of the vectors**, it is invariant to scale or absolute position, making it ideal for comparing movements between people of different sizes or when your camera is at a slightly different distance.

This approach allows the trainer to focus on **alignment and correct posture**, rather than exact positions, giving meaningful feedback even if your limbs are proportionally different from the reference.
