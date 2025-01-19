#!/bin/sh
# --- General DAIC setup ---
#SBATCH --partition=prb,insy,general
#SBATCH --qos=short
#SBATCH --output=render_cubes-%x-%j.out
#SBATCH --error=render_cubes-%x-%j.err

# --- Setup specific for task ---
#SBATCH --job-name=render_cubes_bouncing  # OR render_cubes_orbiting
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --gpu-bind=closest
#SBATCH --mem=8GB

# --- Email me when job finishes ---
#SBATCH --mail-type=ALL
#SBATCH --mail-user=a.baltaretu@student.tudelft.nl

config=scene_info.config          # Path to config file

